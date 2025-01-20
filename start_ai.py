import numpy as np
import speech_recognition as sr
import whisper
import torch
import pyttsx3
import json
import os

from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform
from threading import Thread, Event as ThreadingEvent
from openai import OpenAI
from dotenv import load_dotenv

class AITranscriber(Thread):
    audio_model = None
    recorder = None
    source = None
    transcribe_queue = Queue()
    transcription = ['']
    completed_transcription = None
    record_timeout = 2
    phrase_timeout = 5
    stop_listening_callback = None
    wake_word = "max"
    should_listen = True

    def __init__(self, completed_transcription , audo_model, recorder, source, record_timeout, phrase_timeout, wake_word):
        Thread.__init__(self)
        self.completed_transcription = completed_transcription
        self.audio_model = audo_model
        self.recorder = recorder
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        self.source = source
        self.wake_word = wake_word
        self.stop_phrase = self.wake_word + " stop"
        with self.source:
            recorder.adjust_for_ambient_noise(self.source)

    def run(self): 
        print("starting to listen..")
        phrase_time = None
        if self.stop_listening_callback is None:
            print("turning on listening")
            self.stop_listening_callback = self.recorder.listen_in_background(self.source, lambda _, audio: self.transcribe_queue.put(audio.get_raw_data()), phrase_time_limit=self.record_timeout)
        else:
            raise Exception("Already listening") 
        while self.should_listen:
            try:
                now = datetime.utcnow()
                # Pull raw recorded audio from the queue.
                if not self.transcribe_queue.empty():
                    phrase_complete = False
                    # If enough time has passed between recordings, consider the phrase complete.
                    # Clear the current working audio buffer to start over with the new data.
                    if phrase_time and now - phrase_time > timedelta(seconds=self.phrase_timeout):
                        phrase_complete = True
                    # This is the last time we received new audio data from the queue.
                    phrase_time = now
                    
                    # Combine audio data from queue
                    audio_data = b''.join(self.transcribe_queue.queue)
                    print("clearing transcription queue")
                    self.transcribe_queue.queue.clear()
                    
                    # Convert in-ram buffer to something the model can use directly without needing a temp file.
                    # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                    # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                    # Read the transcription.
                    print("transcribing..")
                    result = self.audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                    text = result['text'].strip()
                    print("transcribing complete with text.." + text)

                    if self.stop_phrase.lower() in text.lower():
                        print("found stop phrase..terminating")
                        self.should_listen = False

                    # If we detected a pause between recordings, add a new item to our transcription.
                    # Otherwise edit the existing one.
                    elif phrase_complete:
                        self.transcription.append(text)
                        # only consider phrases with wake word for further processing
                        if self.wake_word.lower() in text.lower():
                            print("found wake word")
                            self.completed_transcription.put(text)
                        else:
                            print("no wake word")
                            print(text)
                        
                    else:
                        self.transcription[-1] = text
                else:
                    sleep(0.01)
            except KeyboardInterrupt:
                self.stop_listening()
                break
        if self.should_listen == False:
            self.stop_listening()
    
    def stop_listening(self):
        if self.stop_listening_callback is not None:
            self.stop_listening_callback()
            self.stop_listening_callback = None
        else:
            raise Exception("Not listening")


class AITranscriptionProcessor(Thread):
    transcription_queue = None
    thread_count = 2
    stop_event = None
    ai_client = None
    assistant_id = None
    
    def __init__(self, transcription_queue, ai_client, assistant_id):
        Thread.__init__(self)
        self.transcription_queue = transcription_queue
        self.stop_event = ThreadingEvent()
        self.ai_client = ai_client
        self.assistant_id = assistant_id
        self.chat_thread = self.ai_client.beta.threads.create()
        self.thread_count = 2
    
    def run(self):
        print("starting transcription processor..")
        while not self.stop_event.is_set():
            if not self.transcription_queue.empty():
                fetched_transcription = self.transcription_queue.get()
                print("fetching transcription..")
                print(fetched_transcription)
                self.converse_with_ai(fetched_transcription)
                self.transcription_queue.task_done()
            else:
                sleep(0.01)
    
    def converse_with_ai(self, message: str):
        print("conversing with AI..")
        message = self.ai_client.beta.threads.messages.create(
            thread_id=self.chat_thread.id,
            role="user",
            content=message
        )
        run = self.ai_client.beta.threads.runs.create_and_poll(
            thread_id=self.chat_thread.id,
            assistant_id=self.assistant_id,
        )
        if run.status == 'completed': 
            messages = self.ai_client.beta.threads.messages.list(
                thread_id=self.chat_thread.id
            )
            print("all messages..")
            print(messages)

            for message in messages.data:
                if message.role == 'assistant':
                    for block in message.content:
                        if block.type == 'text':
                            value = block.text.value
                            print("message from AI..")
                            print(value)
                            try:
                                #todo: add more processing here
                                value = json.loads(value) # convert to dict
                                #speech_engine = pyttsx3.init()
                                print("saying.." + str(value['answer']))
                                #speech_engine.say(str(value['answer']))
                                #speech_engine.runAndWait()
                                return value
                            except Exception as e:
                                return str(value)
                    break
    
    def stop(self):
        self.stop_event.set()


def main():
    print("initializing..")
    load_dotenv()
    recorder = sr.Recognizer()
    recorder.energy_threshold = 1000
    recorder.dynamic_energy_threshold = False

    source = sr.Microphone(sample_rate=16000)

    audio_model = whisper.load_model("tiny")
    print("model loaded..")

    record_timeout = 2 #how real time recording
    phrase_timeout = 3 #empty space between recordings
    wake_word = "max"
    api_key =os.getenv("OPENAI_API_KEY")
    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
    transcription_queue = Queue()

    transcriber = AITranscriber(transcription_queue, audio_model, recorder, source, record_timeout, phrase_timeout, wake_word)
    transcription_processor = AITranscriptionProcessor(transcription_queue, OpenAI(api_key=api_key, timeout=30), assistant_id)
    try:
        transcriber.start()
        transcription_processor.start()
        transcriber.join()
        print("transcriber joined")
        transcription_processor.stop()
        transcription_processor.join()
        print("transcription processor joined")
    except Exception as e:
        print(f"\033[31mERROR: {e}")

if __name__ == "__main__":
    main()