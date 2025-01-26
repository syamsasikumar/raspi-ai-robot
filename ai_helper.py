import json
import pyaudio

from openai import OpenAI


class AIHelper:
    def __init__(
        self,
        ai_client: OpenAI,
        assistant_id: str,
    ):
        self.ai_client = ai_client
        self.assistant_id = assistant_id
        self.chat_thread = self.ai_client.beta.threads.create()
        self.player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    def converse_with_text(self, imput_text: str):
        print("conversing with AI..")
        self.ai_client.beta.threads.messages.create(
            thread_id=self.chat_thread.id, role="user", content=imput_text
        )
        run = self.ai_client.beta.threads.runs.create_and_poll(
            thread_id=self.chat_thread.id,
            assistant_id=self.assistant_id,
        )
        return self._parse_response(run)

    def converse_with_image(self, imput_text: str, image_path: str):
        print("uploading image..")
        img_file = self.ai_client.files.create(
                    file=open(image_path, "rb"),
                    purpose="vision"
                )
        print("creating thread..")
        self.ai_client.beta.threads.messages.create(
            thread_id= self.chat_thread.id,
            role="user",
            content= [
                {
                    "type": "text",
                    "text": imput_text
                },
                {
                    "type": "image_file",
                    "image_file": {"file_id": img_file.id}
                }
            ],
        )
        print("conversing with AI..")
        run = self.ai_client.beta.threads.runs.create_and_poll(
            thread_id=self.chat_thread.id,
            assistant_id=self.assistant_id,
        )
        return self._parse_response(run)
    
    def _parse_response(self, run):
        if run.status == "completed":
            messages = self.ai_client.beta.threads.messages.list(
                thread_id=self.chat_thread.id
            )
            print("all messages..")
            print(messages)

            for message in messages.data:
                if message.role == "assistant":
                    for block in message.content:
                        if block.type == "text":
                            value = block.text.value
                            print("message from AI..")
                            print(value)
                            try:
                                return json.loads(value)
                            except Exception as e:
                                print("cannot parse AI response :" + value + ":" + e)
                    break

    def speak_using_ai(self, text: str):
        if self.ai_client is None:
            raise Exception("client not initialized to speak with AI")
        with self.ai_client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="nova",
            response_format="pcm",
            input=text,
        ) as response:
            for chunk in response.iter_bytes(chunk_size=1024):
                self.player_stream.write(chunk)