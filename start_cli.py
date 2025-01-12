from vilib import Vilib
from time import sleep
from robot_hat import Music,TTS
import readchar
from os import geteuid
from robot import RobotMovement, RobotSound, RobotCamera
from menu import show_main_menu, show_move_menu, show_camera_menu, show_sound_menu

if geteuid() != 0:
    print(f"\033[0;33m{'The program needs to be run using sudo, otherwise there may be no sound.'}\033[0m")

music = Music()
tts = TTS()

def move_options_cli():
    try:
        robot = RobotMovement()
        while True:
            show_move_menu()
            key = readchar.readkey()
            key = key.lower()
            if key in('wsadikjl'): 
                if 'w' == key:
                    robot.forward()
                elif 's' == key:
                    robot.backward()
                elif 'a' == key:
                    robot.left()
                elif 'd' == key:
                    robot.right()
                elif 'i' == key:
                    robot.head_up()
                elif 'k' == key:
                    robot.head_down()
                elif 'l' == key:
                    robot.head_right()
                elif 'j' == key:
                    robot.head_left()                  
                sleep(0.5)
            elif key == 'r':
                robot.stop()
                return

    finally:
        robot.stop()
        sleep(.2)

def camera_options_cli():
    robot = RobotCamera()
    while True:
        show_camera_menu()
        # readkey
        key = readchar.readkey()
        key = key.lower()
        # take photo
        if key == 'p':
            robot.take_photo()
        # color detect
        elif key != '' and key in ('0123456'):  # '' in ('0123') -> True
            robot.color_detect(int(key))
        # face detection
        elif key =="f":
            robot.face_detect()
        # qrcode detection
        elif key =="q":
            robot.qrcode_detect_switch()
        # show detected object information
        elif key == "s":
            robot.object_show()
        elif key == 'r':
            robot.stop()
            return
        sleep(0.5)

def sound_options_cli(music: Music, tts: TTS):
    robot = RobotSound(music, tts)
    while True:
        show_sound_menu()
        key = readchar.readkey()
        key = key.lower()
        if key == "q":
            robot.play_music()
        elif key == readchar.key.SPACE:
            robot.play_sound_effect()
        elif key == "c":
            robot.play_sound_effect_threading()
        elif key == "t":
            robot.text_to_speak()
        elif key == 'r':
            robot.stop_music()
            return

if __name__ == "__main__":
    music.music_set_volume(20)
    tts.lang("en-US")
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    show_main_menu()
    while True:
        key = readchar.readkey()
        key = key.lower()
        if key in('123'): 
            if '1' == key:
                move_options()
            elif '2' == key:
                sound_options(music, tts) 
            elif '3' == key:
                camera_options() 
            show_main_menu()                     
            sleep(0.5)
        
        elif key == readchar.key.CTRL_C:
            print("\n Quit")
            break
