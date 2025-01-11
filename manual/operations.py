from picarx import Picarx
from pydoc import text
from vilib import Vilib
from time import sleep, time, strftime, localtime
import threading
import os
from robot_hat import Music,TTS
import readchar
from os import geteuid

if geteuid() != 0:
    print(f"\033[0;33m{'The program needs to be run using sudo, otherwise there may be no sound.'}\033[0m")

music = Music()
tts = TTS()
flag_face = False
flag_color = False
qr_code_flag = False

camera_manual = '''
Input key to call the function!
    p: Take photo
    1: Color detect : red
    2: Color detect : orange
    3: Color detect : yellow
    4: Color detect : green
    5: Color detect : blue
    6: Color detect : purple
    0: Switch off Color detect
    q: Scan the QR code
    f: Switch ON/OFF face detect
    s: Display detected object information
    r: Return to main menu
'''

move_manual = '''
Press keys on keyboard to control PiCar-X!
    w: Forward
    a: Turn left
    s: Backward
    d: Turn right
    i: Head up
    k: Head down
    j: Turn head left
    l: Turn head right
    r: Return to main menu
'''

sound_manual = '''
Input key to call the function!
    space: Play sound effect (Car horn)
    c: Play sound effect with threads
    t: Text to speak
    q: Play/Stop Music
    r: Return to main menu
'''

main_manual = '''
Input key to see options!
    1: Car movement options
    2: Sound options
    3: Camera Options
    ctrl+c: Press twice to exit the program
'''

def show_move_menu():
    print("\033[H\033[J",end='')  # clear terminal windows
    print(move_manual)

def show_sound_menu():
    print("\033[H\033[J",end='')  # clear terminal windows
    print(sound_manual)

def show_camera_menu():
    print("\033[H\033[J",end='')  # clear terminal windows
    print(camera_manual)

def show_main_menu():
    print("\033[H\033[J",end='')  # clear terminal windows
    print(main_manual)

color_list = ['close', 'red', 'orange', 'yellow',
        'green', 'blue', 'purple',
]

def face_detect(flag):
    print("Face Detect:" + str(flag))
    Vilib.face_detect_switch(flag)


def qrcode_detect():
    global qr_code_flag
    if qr_code_flag == True:
        Vilib.qrcode_detect_switch(True)
        print("Waitting for QR code")

    text = None
    while True:
        temp = Vilib.detect_obj_parameter['qr_data']
        if temp != "None" and temp != text:
            text = temp
            print('QR code:%s'%text)
        if qr_code_flag == False:
            break
        sleep(0.5)
    Vilib.qrcode_detect_switch(False)


def take_photo():
    _time = strftime('%Y-%m-%d-%H-%M-%S',localtime(time()))
    name = 'photo_%s'%_time
    username = os.getlogin()

    path = f"/home/{username}/Pictures/"
    Vilib.take_photo(name, path)
    print('photo save as %s%s.jpg'%(path,name))


def object_show():
    global flag_color, flag_face

    if flag_color is True:
        if Vilib.detect_obj_parameter['color_n'] == 0:
            print('Color Detect: None')
        else:
            color_coodinate = (Vilib.detect_obj_parameter['color_x'],Vilib.detect_obj_parameter['color_y'])
            color_size = (Vilib.detect_obj_parameter['color_w'],Vilib.detect_obj_parameter['color_h'])
            print("[Color Detect] ","Coordinate:",color_coodinate,"Size",color_size)

    if flag_face is True:
        if Vilib.detect_obj_parameter['human_n'] == 0:
            print('Face Detect: None')
        else:
            human_coodinate = (Vilib.detect_obj_parameter['human_x'],Vilib.detect_obj_parameter['human_y'])
            human_size = (Vilib.detect_obj_parameter['human_w'],Vilib.detect_obj_parameter['human_h'])
            print("[Face Detect] ","Coordinate:",human_coodinate,"Size",human_size)

def move_options():
    try:
        pan_angle = 0
        tilt_angle = 0
        px = Picarx()
        show_move_menu()
        while True:
            key = readchar.readkey()
            key = key.lower()
            if key in('wsadikjl'): 
                if 'w' == key:
                    px.set_dir_servo_angle(0)
                    px.forward(80)
                elif 's' == key:
                    px.set_dir_servo_angle(0)
                    px.backward(80)
                elif 'a' == key:
                    px.set_dir_servo_angle(-30)
                    px.forward(80)
                elif 'd' == key:
                    px.set_dir_servo_angle(30)
                    px.forward(80)
                elif 'i' == key:
                    tilt_angle+=5
                    if tilt_angle>30:
                        tilt_angle=30
                elif 'k' == key:
                    tilt_angle-=5
                    if tilt_angle<-30:
                        tilt_angle=-30
                elif 'l' == key:
                    pan_angle+=5
                    if pan_angle>30:
                        pan_angle=30
                elif 'j' == key:
                    pan_angle-=5
                    if pan_angle<-30:
                        pan_angle=-30                 

                px.set_cam_tilt_angle(tilt_angle)
                px.set_cam_pan_angle(pan_angle)      
                show_move_menu()                     
                sleep(0.5)
                px.forward(0)
          
            elif key == 'r':
                px.set_cam_tilt_angle(0)
                px.set_cam_pan_angle(0)  
                px.set_dir_servo_angle(0)  
                px.stop()
                return

    finally:
        px.set_cam_tilt_angle(0)
        px.set_cam_pan_angle(0)  
        px.set_dir_servo_angle(0)  
        px.stop()
        sleep(.2)

def sound_options():
    flag_bgm = False
    while True:
        show_sound_menu()
        key = readchar.readkey()
        key = key.lower()
        if key == "q":
            flag_bgm = not flag_bgm
            if flag_bgm is True:
                print('Play Music')
                music.music_play('../sounds/slow-trail-Ahjay_Stelino.mp3')
            else:
                print('Stop Music')
                music.music_stop()

        elif key == readchar.key.SPACE:
            print('Beep beep beep !')
            music.sound_play('../sounds/car-double-horn.wav')
            sleep(0.05)

        elif key == "c":
            print('Beep beep beep !')
            music.sound_play_threading('../sounds/car-double-horn.wav')
            sleep(0.05)

        elif key == "t":
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
            tts.say(sentence)

        elif key == 'r':
            return

def camera_options():
    global flag_face, flag_color, qr_code_flag
    qrcode_thread = None
    show_camera_menu()

    while True:
        # readkey
        key = readchar.readkey()
        key = key.lower()
        # take photo
        if key == 'p':
            take_photo()
        # color detect
        elif key != '' and key in ('0123456'):  # '' in ('0123') -> True
            index = int(key)
            if index == 0:
                flag_color = False
                Vilib.color_detect('close')
            else:
                flag_color = True
                Vilib.color_detect(color_list[index]) # color_detect(color:str -> color_name/close)
            print('Color detect : %s'%color_list[index])
        # face detection
        elif key =="f":
            flag_face = not flag_face
            face_detect(flag_face)
        # qrcode detection
        elif key =="q":
            qr_code_flag = not qr_code_flag
            if qr_code_flag == True:
                if qrcode_thread == None or not qrcode_thread.is_alive():
                    qrcode_thread = threading.Thread(target=qrcode_detect)
                    qrcode_thread.daemon = True
                    qrcode_thread.start()
            else:
                if qrcode_thread != None and qrcode_thread.is_alive():
                # wait for thread to end
                    qrcode_thread.join()
                    print('QRcode Detect: close')
        # show detected object information
        elif key == "s":
            object_show()
        elif key == 'r':
            return
        sleep(0.5)

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
                sound_options() 
            elif '3' == key:
                camera_options() 
            show_main_menu()                     
            sleep(0.5)
        
        elif key == readchar.key.CTRL_C:
            print("\n Quit")
            break
