import os
import re
import threading
from time import localtime, sleep, strftime, time
from typing import Optional

import readchar
import pyaudio
from picamera2 import Picamera2
from picarx import Picarx
from robot_hat import Music
from vilib import Vilib
from ai_helper import AIHelper

from menu import show_sound_menu


class RobotMovement:
    robot = None
    tile_angle = 0
    pan_angle = 0

    def __init__(self):
        self.robot = Picarx()

    def forward(self):
        self.robot.set_dir_servo_angle(0)
        self.robot.forward(80)
        sleep(0.5)
        self.robot.forward(0)

    def backward(self):
        self.robot.set_dir_servo_angle(0)
        self.robot.backward(80)
        sleep(0.5)
        self.robot.forward(0)

    def left(self):
        self.robot.set_dir_servo_angle(-30)
        self.robot.forward(80)
        sleep(0.5)
        self.robot.forward(0)

    def right(self):
        self.robot.set_dir_servo_angle(30)
        self.robot.forward(80)
        sleep(0.5)
        self.robot.forward(0)

    def head_up(self):
        self.tilt_angle += 5
        if self.tilt_angle > 30:
            self.tilt_angle = 30
        self.robot.set_cam_tilt_angle(self.tilt_angle)

    def head_down(self):
        self.tilt_angle -= 5
        if self.tilt_angle < -30:
            self.tilt_angle = -30
        self.robot.set_cam_tilt_angle(self.tilt_angle)

    def head_left(self):
        self.pan_angle += 5
        if self.pan_angle > 30:
            self.pan_angle = 30
        self.robot.set_cam_pan_angle(self.pan_angle)

    def head_right(self):
        self.pan_angle -= 5
        if self.pan_angle < -30:
            self.pan_angle = -30
        self.robot.set_cam_pan_angle(self.pan_angle)

    def stop(self):
        self.robot.forward(0)
        self.robot.set_cam_tilt_angle(0)
        self.robot.set_cam_pan_angle(0)
        self.robot.set_dir_servo_angle(0)
        self.robot.stop()

    def rub_hands(self):
        self.robot.reset()
        for i in range(5):
            self.robot.set_dir_servo_angle(-6)
            sleep(0.5)
            self.robot.set_dir_servo_angle(6)
            sleep(0.5)
        self.robot.reset()

    def think(self):
        self.robot.reset()

        for i in range(11):
            self.robot.set_cam_pan_angle(i * 3)
            self.robot.set_cam_tilt_angle(-i * 2)
            self.robot.set_dir_servo_angle(i * 2)
            sleep(0.05)
        sleep(1)
        self.robot.set_cam_pan_angle(15)
        self.robot.set_cam_tilt_angle(-10)
        self.robot.set_dir_servo_angle(10)
        sleep(0.1)
        self.robot.reset()

    def shake_head(self):
        self.robot.stop()
        self.robot.set_cam_pan_angle(0)
        self.robot.set_cam_pan_angle(60)
        sleep(0.2)
        self.robot.set_cam_pan_angle(-50)
        sleep(0.1)
        self.robot.set_cam_pan_angle(40)
        sleep(0.1)
        self.robot.set_cam_pan_angle(-30)
        sleep(0.1)
        self.robot.set_cam_pan_angle(20)
        sleep(0.1)
        self.robot.set_cam_pan_angle(-10)
        sleep(0.1)
        self.robot.set_cam_pan_angle(10)
        sleep(0.1)
        self.robot.set_cam_pan_angle(-5)
        sleep(0.1)
        self.robot.set_cam_pan_angle(0)

    def nod(self):
        self.robot.reset()
        self.robot.set_cam_tilt_angle(0)
        self.robot.set_cam_tilt_angle(5)
        sleep(0.1)
        self.robot.set_cam_tilt_angle(-30)
        sleep(0.1)
        self.robot.set_cam_tilt_angle(5)
        sleep(0.1)
        self.robot.set_cam_tilt_angle(-30)
        sleep(0.1)
        self.robot.set_cam_tilt_angle(0)


class RobotSoundOut:
    music = None
    flag_bgm = False

    def __init__(self, music: Music, ai_helper: AIHelper):
        self.music = music
        self.ai_helper = ai_helper

    def play_music(self):
        self.flag_bgm = not self.flag_bgm
        if self.flag_bgm is True:
            print("Play Music")
            self.music.music_play("./sounds/slow-trail-Ahjay_Stelino.mp3")
        else:
            print("Stop Music")
            self.music.music_stop()

    def play_sound_effect(self):
        print("Beep beep beep !")
        self.music.sound_play("./sounds/car-double-horn.wav")

    def play_sound_effect_threading(self):
        print("Beep beep beep !")
        self.music.sound_play_threading("./sounds/car-double-horn.wav")

    def text_to_speak(self):
        sentence = ""
        while True:
            show_sound_menu()
            print("Type sentence to read out, press enter to terminate!")
            print(sentence)
            char = readchar.readchar()
            if char == readchar.key.BACKSPACE:
                sentence = sentence[:-1]
            elif char == readchar.key.ENTER:
                break
            else:
                sentence += char
        self.speak_using_ai(sentence)

    def stop_music(self):
        if self.flag_bgm is True:
            self.music.music_stop()

    def speak_using_ai(self, text: str):
        self.ai_helper.speak_using_ai(text)


class RobotCamera:
    flag_face = False
    flag_color = False
    flag_qr_code = False
    color_list = ["close", "red", "orange", "yellow", "green", "blue", "purple"]
    qrcode_thread = None

    def __init__(self, camera: Optional[Picamera2]):
        self.camera = camera
        if self.camera is not None:
            self.camera.start()
            sleep(2)

    def qr_code_detect(self):
        if self.flag_qr_code is True:
            Vilib.qrcode_detect_switch(True)
            print("Waitting for QR code")

        text = None
        while True:
            temp = Vilib.detect_obj_parameter["qr_data"]
            if temp not in ("None", text):
                text = temp
                print("QR code:%s" % text)
            if self.flag_qr_code is False:
                break
            sleep(0.5)
        Vilib.qrcode_detect_switch(False)

    def take_photo_without_picamera(self):
        _time = strftime("%Y-%m-%d-%H-%M-%S", localtime(time()))
        name = "photo_%s" % _time
        username = os.getlogin()

        path = f"/home/{username}/Pictures/"
        Vilib.take_photo(name, path)
        print("photo save as %s%s.jpg" % (path, name))
        return path + name + ".jpg"

    def take_photo(self):
        _time = strftime("%Y-%m-%d-%H-%M-%S", localtime(time()))
        name = "photo_%s" % _time
        username = os.getlogin()
        path = f"/home/{username}/Pictures/"
        file_name = path + name + ".jpg"
        self.camera.capture_file(file_name)
        return file_name

    def object_show(self):
        if self.flag_color is True:
            if Vilib.detect_obj_parameter["color_n"] == 0:
                print("Color Detect: None")
            else:
                color_coodinate = (
                    Vilib.detect_obj_parameter["color_x"],
                    Vilib.detect_obj_parameter["color_y"],
                )
                color_size = (
                    Vilib.detect_obj_parameter["color_w"],
                    Vilib.detect_obj_parameter["color_h"],
                )
                print(
                    "[Color Detect] ",
                    "Coordinate:",
                    color_coodinate,
                    "Size",
                    color_size,
                )

        if self.flag_face is True:
            if Vilib.detect_obj_parameter["human_n"] == 0:
                print("Face Detect: None")
            else:
                human_coodinate = (
                    Vilib.detect_obj_parameter["human_x"],
                    Vilib.detect_obj_parameter["human_y"],
                )
                human_size = (
                    Vilib.detect_obj_parameter["human_w"],
                    Vilib.detect_obj_parameter["human_h"],
                )
                print(
                    "[Face Detect] ", "Coordinate:", human_coodinate, "Size", human_size
                )

    def color_detect(self, key: int):
        if key == 0:
            self.flag_color = False
            Vilib.color_detect("close")
        else:
            self.flag_color = True
            Vilib.color_detect(
                self.color_list[key]
            )  # color_detect(color:str -> color_name/close)
        print("Color detect : %s" % self.color_list[key])

    def face_detect(self):
        self.flag_face = not self.flag_face
        Vilib.face_detect_switch(self.face_detect)

    def qrcode_detect_switch(self):
        self.flag_qr_code = not self.flag_qr_code
        if self.flag_qr_code is True:
            if self.qrcode_thread is None or not self.qrcode_thread.is_alive():
                self.qrcode_thread = threading.Thread(target=self.qr_code_detect)
                self.qrcode_thread.daemon = True
                self.qrcode_thread.start()
        else:
            if self.qrcode_thread is not None and self.qrcode_thread.is_alive():
                # wait for thread to end
                self.qrcode_thread.join()
                print("QRcode Detect: close")

    def stop(self):
        self.flag_face = False
        self.flag_color = False
        self.flag_qr_code = False
        Vilib.face_detect_switch(False)
        Vilib.color_detect("close")
        Vilib.qrcode_detect_switch(False)
        if self.qrcode_thread is not None and self.qrcode_thread.is_alive():
            # wait for thread to end
            self.qrcode_thread.join()
            print("QRcode Detect: close")

    def close(self):
        self.stop()
        Vilib.camera_close()
