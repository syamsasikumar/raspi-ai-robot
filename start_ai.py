import os
from queue import Queue

import speech_recognition as sr
import whisper
from dotenv import load_dotenv
from openai import OpenAI
from ai_helper import AIHelper

from ai import (ActionHandler, MessageHandler, Transcriber,
                TranscriptionProcessor)
from robot_client import RobotClient


def get_rpc_channel():
    load_dotenv()
    if os.getenv("RPC_SERVER_MODE") == "local":
        return os.getenv("RPC_LOCAL_CHANNEL")
    return os.getenv("RPC_CHANNEL")


def main():
    print("initializing..")
    load_dotenv()
    recorder = sr.Recognizer()
    recorder.energy_threshold = 1000
    recorder.dynamic_energy_threshold = False

    source = sr.Microphone(sample_rate=16000)
    # audio model for parsing speech to text instructions
    audio_model = whisper.load_model("tiny")  # tiny, base, small, medium, large
    print("model loaded..")

    record_timeout = 5  # how real time recording
    phrase_timeout = 3  # empty space between recordings
    # wake word to start processing instructions, instructions without wake word are ignored
    wake_word = os.getenv("WAKE_WORD")
    kill_phrase = os.getenv("KILL_SWITCH_PHRASE")
    api_key = os.getenv("OPENAI_API_KEY")
    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
    rpc_channel = get_rpc_channel()
    transcription_queue = Queue()  # queue to hold transcriptions for AI processing
    action_queue = Queue()  # queue to hold actions for robot
    message_queue = Queue()  # queue to hold messages for robot to speak
    robot_client = RobotClient(rpc_channel)
    openai = OpenAI(api_key=api_key, timeout=30)
    ai_helper = AIHelper(openai, assistant_id)

    transcriber = Transcriber(
        transcription_queue,
        audio_model,
        recorder,
        source,
        record_timeout,
        phrase_timeout,
        wake_word,
        kill_phrase,
    )
    transcription_processor = TranscriptionProcessor(
        transcription_queue,
        ai_helper,
        message_queue,
        action_queue,
    )
    message_handler = MessageHandler(message_queue, robot_client)
    action_handler = ActionHandler(action_queue, robot_client)
    try:
        transcriber.start()
        transcription_processor.start()
        message_handler.start()
        action_handler.start()
        transcriber.join()
        transcription_processor.stop()
        transcription_processor.join()
        message_handler.stop()
        message_handler.join()
        action_handler.stop()
        action_handler.join()
    except Exception as e:
        print(f"\033[31mERROR: {e}")


if __name__ == "__main__":
    main()
