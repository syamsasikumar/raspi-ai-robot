import os
from os import geteuid
from time import sleep

import readchar
from dotenv import load_dotenv
from openai import OpenAI
from robot_hat import Music
from vilib import Vilib

from ai_helper import AIHelper
from menu import (show_camera_menu, show_main_menu, show_move_menu,
                  show_sound_menu)
from robot import RobotCamera, RobotMovement, RobotSoundOut

if geteuid() != 0:
    print(
        f"\033[0;33m{'The program needs to be run using sudo, otherwise there may be no sound.'}\033[0m"
    )

music = Music()

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
openai = OpenAI(api_key=api_key, timeout=30)
ai_helper = AIHelper(openai, assistant_id)

def move_options_cli():
    try:
        robot = RobotMovement()
        while True:
            show_move_menu()
            key = readchar.readkey().lower()
            if key in ("wsadikjl"):
                if "w" == key:
                    robot.forward()
                elif "s" == key:
                    robot.backward()
                elif "a" == key:
                    robot.left()
                elif "d" == key:
                    robot.right()
                elif "i" == key:
                    robot.head_up()
                elif "k" == key:
                    robot.head_down()
                elif "l" == key:
                    robot.head_right()
                elif "j" == key:
                    robot.head_left()
                sleep(0.5)
            elif key == "r":
                robot.stop()
                return

    finally:
        robot.stop()
        sleep(0.2)


def camera_options_cli():
    robot = RobotCamera(None)
    while True:
        show_camera_menu()
        # readkey
        key = readchar.readkey().lower()
        # take photo
        if key == "p":
            robot.take_photo()
        # color detect
        elif key != "" and key in ("0123456"):  # '' in ('0123') -> True
            robot.color_detect(int(key))
        # face detection
        elif key == "f":
            robot.face_detect()
        # qrcode detection
        elif key == "q":
            robot.qrcode_detect_switch()
        # show detected object information
        elif key == "s":
            robot.object_show()
        elif key == "r":
            robot.stop()
            return
        elif key == "i":
            print("capturing image..")
            image_path = robot.take_photo_without_picamera()
            print("sending image for processing..")
            print("image path.." + image_path)
            response = ai_helper.converse_with_image("what do you see?", image_path)
            if "actions" in response:
                print("actions from image.." + str(response["actions"]))
            if "answer" in response:
                print("saying.." + str(response["answer"]))
            if "actions" not in response and "answer" not in response:
                print(
                    "no answer or action found in response " + response
                )
        sleep(0.5)


def sound_options_cli(music: Music):
    robot = RobotSoundOut(music, ai_helper)
    while True:
        show_sound_menu()
        key = readchar.readkey().lower()
        if key == "q":
            robot.play_music()
        elif key == readchar.key.SPACE:
            robot.play_sound_effect()
        elif key == "c":
            robot.play_sound_effect_threading()
        elif key == "t":
            robot.text_to_speak()
        elif key == "r":
            robot.stop_music()
            return


if __name__ == "__main__":
    music.music_set_volume(20)
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=True, web=True)
    show_main_menu()
    while True:
        key = readchar.readkey()
        key = key.lower()
        if key in ("123"):
            if "1" == key:
                move_options_cli()
            elif "2" == key:
                sound_options_cli(music)
            elif "3" == key:
                camera_options_cli()
            show_main_menu()
            sleep(0.5)

        elif key == readchar.key.CTRL_C:
            print("\n Quit")
            break
