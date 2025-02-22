import os
from concurrent import futures

import grpc
import threading
from dotenv import load_dotenv
from openai import OpenAI
from picamera2 import Picamera2
from robot_hat import Music

from ai_helper import AIHelper
from robot import RobotCamera, RobotMovement, RobotSoundOut
from rpc.robot_pb2 import RobotReply
from rpc.robot_pb2_grpc import RobotServicer, add_RobotServicer_to_server


class RobotServer(RobotServicer):
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        music = Music()
        music.music_set_volume(80)
        camera = Picamera2()
        openai = OpenAI(api_key=api_key, timeout=30)
        self.ai_helper = AIHelper(openai, assistant_id)
        self.robot_movement = RobotMovement()
        self.robot_sound_out = RobotSoundOut(music, self.ai_helper)
        self.robot_camera = RobotCamera(camera)
        print("RobotServer initialized")

    def PerformAction(self, request, context):
        actions = request.actions
        for action in actions:
            # todo
            print("performing action.." + action)
            self._perform_action(action)
        return RobotReply(reply="action performed")

    def SayMessage(self, request, context):
        message = request.message
        print("".join(message))
        self.robot_sound_out.speak_using_ai(str("".join(message)))
        # todo
        return RobotReply(reply="message spoken")

    def _perform_action(self, action: str, ignore_see: bool = False):
        if action == "move forward":
            self.robot_movement.forward()
        elif action == "move backward":
            self.robot_movement.backward()
        elif action == "turn left":
            self.robot_movement.left()
        elif action == "turn right":
            self.robot_movement.right()
        elif action == "play music":
            self.robot_sound_out.play_music()
        elif action == "stop music":
            self.robot_sound_out.stop_music()
        elif action == "free roam":
            self._start_free_roam()
        elif action == "stop free roam":
            self._stop_free_roam()
        elif action == "honk":
            self.robot_sound_out.play_sound_effect()
        elif action == "see" and not ignore_see:
            self._capture_and_process_image("what do you see in this image?")

    def _start_free_roam(self):
        if self.robot_movement.is_in_free_roam_mode():
            return
        self.robot_sound_out.speak_using_ai("I am about to go on an adventure! hold on..")
        free_roam_thread = threading.Thread(target=self.robot_movement.start_free_roam_movement)
        free_roam_thread.start()

    def _stop_free_roam(self):
        if not self.robot_movement.is_in_free_roam_mode():
            return
        self.robot_sound_out.speak_using_ai("Alright! I will stop now..")
        self.robot_movement.stop_free_roam_movement()

    def _capture_and_process_image(self, message: str):
        self.robot_sound_out.speak_using_ai("opening my eyes to see! hold on..")
        print("capturing image..")
        image_path = self.robot_camera.take_photo()
        print("sending image for processing..")
        response = self.ai_helper.converse_with_image(message, image_path)
        if "actions" in response:
            print("actions from image.." + str(response["actions"]))
            for action in response["actions"]:
                self._perform_action(action, ignore_see=True)
        if "answer" in response:
            print("saying.." + str(response["answer"]))
            self.robot_sound_out.speak_using_ai(str("".join(response["answer"])))
        if "actions" not in response and "answer" not in response:
            print("no answer or action found in response " + response)


if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    robot_server = RobotServer()
    add_RobotServicer_to_server(robot_server, server)
    server.add_insecure_port("0.0.0.0:50051")
    server.start()
    server.wait_for_termination()
