from picarx import Picarx
from menu import show_sound_menu
import readchar
from robot_hat import Music,TTS
from vilib import Vilib
from time import sleep
from time import sleep, time, strftime, localtime
import threading
import os

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
        self.tilt_angle+=5
        if self.tilt_angle>30:
            self.tilt_angle=30
        self.robot.set_cam_tilt_angle(self.tilt_angle)

    def head_down(self):
        self.tilt_angle-=5
        if self.tilt_angle<-30:
            self.tilt_angle=-30
        self.robot.set_cam_tilt_angle(self.tilt_angle) 

    def head_left(self):
        self.pan_angle+=5
        if self.pan_angle>30:
            self.pan_angle=30
        self.robot.set_cam_pan_angle(self.pan_angle)

    def head_right(self):
        self.pan_angle-=5
        if self.pan_angle<-30:
            self.pan_angle=-30
        self.robot.set_cam_pan_angle(self.pan_angle)

    def stop(self):
        self.robot.forward(0)
        self.robot.set_cam_tilt_angle(0)
        self.robot.set_cam_pan_angle(0)  
        self.robot.set_dir_servo_angle(0)  
        self.robot.stop()

class RobotSoundOut:
    music = None
    tts = None
    flag_bgm = False

    def __init__(self, music: Music, tts: TTS):
        self.music = music
        self.tts = tts
    
    def play_music(self):
        self.flag_bgm = not self.flag_bgm
        if self.flag_bgm is True:
            print('Play Music')
            self.music.music_play('./sounds/slow-trail-Ahjay_Stelino.mp3')
        else:
            print('Stop Music')
            self.music.music_stop()
    
    def play_sound_effect(self):
        print('Beep beep beep !')
        self.music.sound_play('./sounds/car-double-horn.wav')
    
    def play_sound_effect_threading(self):
        print('Beep beep beep !')
        self.music.sound_play_threading('./sounds/car-double-horn.wav')
    
    def text_to_speak(self):
        sentence = ''
        while True:
            show_sound_menu()
            print('Type sentence to read out, press enter to terminate!')
            print(sentence)
            char = readchar.readchar()
            if char == readchar.key.BACKSPACE:
                sentence = sentence[:-1]
            elif char == readchar.key.ENTER:
                break
            else:
                sentence += char
        self.speak(sentence)
    
    def speak(self, sentence:str):
        self.tts.say(sentence)
    
    def stop_music(self):
        if self.flag_bgm is True:
           self.music.music_stop() 

class RobotCamera:
    flag_face = False
    flag_color = False
    flag_qr_code = False
    color_list = ['close', 'red', 'orange', 'yellow',
        'green', 'blue', 'purple']
    qrcode_thread = None

    def __init__(self):
        pass

    def qr_code_detect(self):
        if self.qr_code_flag == True:
            Vilib.qrcode_detect_switch(True)
            print("Waitting for QR code")

        text = None
        while True:
            temp = Vilib.detect_obj_parameter['qr_data']
            if temp != "None" and temp != text:
                text = temp
                print('QR code:%s'%text)
            if self.qr_code_flag == False:
                break
            sleep(0.5)
        Vilib.qrcode_detect_switch(False)
    
    def take_photo(self):
        _time = strftime('%Y-%m-%d-%H-%M-%S',localtime(time()))
        name = 'photo_%s'%_time
        username = os.getlogin()

        path = f"/home/{username}/Pictures/"
        Vilib.take_photo(name, path)
        print('photo save as %s%s.jpg'%(path,name))

    def object_show(self):
        if self.flag_color is True:
            if Vilib.detect_obj_parameter['color_n'] == 0:
                print('Color Detect: None')
            else:
                color_coodinate = (Vilib.detect_obj_parameter['color_x'],Vilib.detect_obj_parameter['color_y'])
                color_size = (Vilib.detect_obj_parameter['color_w'],Vilib.detect_obj_parameter['color_h'])
                print("[Color Detect] ","Coordinate:",color_coodinate,"Size",color_size)

        if self.flag_face is True:
            if Vilib.detect_obj_parameter['human_n'] == 0:
                print('Face Detect: None')
            else:
                human_coodinate = (Vilib.detect_obj_parameter['human_x'],Vilib.detect_obj_parameter['human_y'])
                human_size = (Vilib.detect_obj_parameter['human_w'],Vilib.detect_obj_parameter['human_h'])
                print("[Face Detect] ","Coordinate:",human_coodinate,"Size",human_size)
    
    def color_detect(self, key:int):
        if key == 0:
            self.flag_color = False
            Vilib.color_detect('close')
        else:
            self.flag_color = True
            Vilib.color_detect(self.color_list[key]) # color_detect(color:str -> color_name/close)
        print('Color detect : %s'%self.color_list[key])
    
    def face_detect(self):
        self.flag_face = not self.flag_face
        Vilib.face_detect_switch(self.face_detect)

    def qrcode_detect_switch(self):
        self.flag_qr_code = not self.flag_qr_code
        if self.flag_qr_code == True:
            if self.qrcode_thread == None or not self.qrcode_thread.is_alive():
                self.qrcode_thread = threading.Thread(target=self.qrcode_detect)
                self.qrcode_thread.daemon = True
                self.qrcode_thread.start()
        else:
            if self.qrcode_thread != None and self.qrcode_thread.is_alive():
                # wait for thread to end
                self.qrcode_thread.join()
                print('QRcode Detect: close')
    
    def stop(self):
        self.flag_face = False
        self.flag_color = False
        self.flag_qr_code = False
        Vilib.face_detect_switch(False)
        Vilib.color_detect('close')
        Vilib.qrcode_detect_switch(False)
        if self.qrcode_thread != None and self.qrcode_thread.is_alive():
            # wait for thread to end
            self.qrcode_thread.join()
            print('QRcode Detect: close')
    
    def close(self):
        self.stop()
        Vilib.camera_close()

class RobotSoundIn:
    def __init__(self):
        pass

    def parse_instructions(self):
        pass




class RobotAI:
    def __init__(self):
        pass

    def process_instructions(self):
        pass

