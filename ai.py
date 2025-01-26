import json
import os
from datetime import datetime, timedelta
from queue import Queue
from threading import Event as ThreadingEvent
from threading import Thread
from time import sleep

import numpy as np
import speech_recognition as sr
import torch
from ai_helper import AIHelper
from speech_recognition import Microphone, Recognizer

from ai_helper import AIHelper
from robot_client import RobotClient


# transcribes speech to text using an audio model (whisper)
class Transcriber(Thread):
    transcribe_queue = Queue()
    transcription = [""]
    stop_listening_callback = None
    should_listen = True

    def __init__(
        self,
        completed_transcriptions: Queue,
        audio_model,
        recorder: Recognizer,
        source: Microphone,
        record_timeout: int,
        phrase_timeout: int,
        wake_word: str,
        stop_phrase: str,
    ):
        Thread.__init__(self)
        self.completed_transcriptions = completed_transcriptions
        self.audio_model = audio_model
        self.recorder = recorder
        self.record_timeout = record_timeout
        self.phrase_timeout = phrase_timeout
        self.source = source
        self.wake_word = wake_word
        self.stop_phrase = stop_phrase
        with self.source:
            recorder.adjust_for_ambient_noise(self.source)

    def run(self):
        print("starting to listen..")
        phrase_time = None
        if self.stop_listening_callback is None:
            print("turning on listening")
            self.stop_listening_callback = self.recorder.listen_in_background(
                self.source,
                lambda _, audio: self.transcribe_queue.put(audio.get_raw_data()),
                phrase_time_limit=self.record_timeout,
            )
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
                    if phrase_time and now - phrase_time > timedelta(
                        seconds=self.phrase_timeout
                    ):
                        phrase_complete = True
                    # This is the last time we received new audio data from the queue.
                    phrase_time = now

                    # Combine audio data from queue
                    audio_data = b"".join(self.transcribe_queue.queue)
                    print("clearing transcription queue")
                    self.transcribe_queue.queue.clear()

                    # Convert in-ram buffer to something the model can use directly without needing a temp file.
                    # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                    # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                    audio_np = (
                        np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
                        / 32768.0
                    )

                    # Read the transcription.
                    print("transcribing..")
                    result = self.audio_model.transcribe(
                        audio_np, fp16=torch.cuda.is_available()
                    )
                    text = result["text"].strip()
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
                            self.completed_transcriptions.put(text)
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


# processes transcriptions using AI to translate to robot actions or audio responses
class TranscriptionProcessor(Thread):
    transcription_queue = None
    thread_count = 2
    stop_event = None

    def __init__(
        self,
        transcription_queue: Queue,
        ai_helper: AIHelper,
        message_queue: Queue,
        action_queue: Queue,
    ):
        Thread.__init__(self)
        self.transcription_queue = transcription_queue
        self.stop_event = ThreadingEvent()
        self.ai_helper = ai_helper
        self.thread_count = 2
        self.message_queue = message_queue
        self.action_queue = action_queue

    def run(self):
        print("starting transcription processor..")
        while not self.stop_event.is_set():
            if not self.transcription_queue.empty():
                fetched_transcription = self.transcription_queue.get()
                print("fetching transcription..")
                print(fetched_transcription)
                self.transcription_queue.task_done()
                self.fetch_and_queue_ai_response(fetched_transcription)
            else:
                sleep(0.01)

    def fetch_and_queue_ai_response(self, message: str):
        response = self.ai_helper.converse_with_text(message)
        mute_message = False
        if "see" in response["actions"]:
            mute_message = True
        if "actions" in response:
            print("saying.." + str(response["actions"]))
            self.action_queue.put(response["actions"])
        if "answer" in response and not mute_message:
            self.message_queue.put(response["answer"])
        if "actions" not in response and "answer" not in response:
            print("no answer or action found in response " + response)

    def stop(self):
        self.stop_event.set()


# handles robot actions from AI responses
class ActionHandler(Thread):
    def __init__(self, action_queue: Queue, robot_client: RobotClient):
        Thread.__init__(self)
        self.action_queue = action_queue
        self.stop_event = ThreadingEvent()
        self.robot_client = robot_client

    def run(self):
        while not self.stop_event.is_set():
            if not self.action_queue.empty():
                fetched_actions = self.action_queue.get()
                print("fetching action..")
                print(fetched_actions)
                self.action_queue.task_done()
                response = self.robot_client.perform_action(fetched_actions)
                print("recieved response" + response)
            else:
                sleep(0.01)

    def stop(self):
        self.stop_event.set()


# handles responses from AI which need to be spoken out
class MessageHandler(Thread):
    def __init__(self, message_queue: Queue, robot_client: RobotClient):
        Thread.__init__(self)
        self.message_queue = message_queue
        self.stop_event = ThreadingEvent()
        self.robot_client = robot_client

    def run(self):
        while not self.stop_event.is_set():
            if not self.message_queue.empty():
                fetched_message = self.message_queue.get()
                print("fetching message..")
                # robot stt is very sensitive to special characters
                fetched_message = (
                    fetched_message.encode("ascii", "ignore")
                    .decode("ascii")
                    .replace("'", "")
                )
                print(fetched_message)
                self.message_queue.task_done()
                response = self.robot_client.say_message(fetched_message)
                print("recieved response" + response)
            else:
                sleep(0.01)

    def stop(self):
        self.stop_event.set()
