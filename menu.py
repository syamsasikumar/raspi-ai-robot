camera_manual = """
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
    i: Capture image and process with AI
    r: Return to main menu
"""

move_manual = """
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
"""

sound_manual = """
Input key to call the function!
    space: Play sound effect (Car horn)
    c: Play sound effect with threads
    t: Text to speak
    q: Play/Stop Music
    r: Return to main menu
"""

main_manual = """
Input key to see options!
    1: Car movement options
    2: Sound options
    3: Camera Options
    ctrl+c: Press twice to exit the program
"""


def show_move_menu():
    print("\033[H\033[J", end="")  # clear terminal windows
    print(move_manual)


def show_sound_menu():
    print("\033[H\033[J", end="")  # clear terminal windows
    print(sound_manual)


def show_camera_menu():
    print("\033[H\033[J", end="")  # clear terminal windows
    print(camera_manual)


def show_main_menu():
    print("\033[H\033[J", end="")  # clear terminal windows
    print(main_manual)
