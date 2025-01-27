# raspi-ai-robot
Python controller for intelligent Raspberry pi robot

Robot uses Raspberry pi 4B + [Sunfounder HAT](https://www.sunfounder.com/products/sunfounder-robot-hat-expansion-board-designed-for-raspberry-pi) module.

## What can the robot do?
Think Alexa on wheels - the robot is capable of
- motion with 2 servos controlling linear and lateral movements
- vision using picamera
- voice activated conversations using wake word e.g. `<robot_name> how do you bake bread?`
- follow natural language instructions e.g. `can you move forward?` or `what do you see?`
- respond with natural-sounding speech

## How does it work?
At a high level it can be broken down into 
- Chat Engine - uses AI to transcribe incoming speech from a user, breaks it down into `actions` for robot to perform and `answers` for robot voice responses. 
- Robot Controller - uses Sunfounder's python modules to interface with the peripherals on robot hat (servos, camera etc) and perform actions. Also uses AI to respond with a natural sounding voice.
- Robot Server - grpc interface for invoking remote instructions for the robot
<img width="880" alt="Screenshot 2025-01-26 at 6 19 53 PM" src="https://github.com/user-attachments/assets/eec82f15-335d-4b38-be62-289522ec123a" />

NOTE - since running whisper locally on my Raspberry pi is not performant, the speech engine needs to run on a separate machine with adequate resources. The `robot_server` module which runs locally on the pi can be used to interface with the robot.

## How can I run this?
One time setup - 
* Install necessary python modules on rpi and the remote machine for running transcription service (see `requirements.txt` and Sunfounder's documentation from the link above)
* create `.env` file (check `.env.example`) to set environment properties

To run in "voice" input mode -
* Run `start_ai.py` on the remote machine to run the local transcription service
* Run `robot_server.py` on rpi
* profit!

A "cli" input mode is also available with elementary functions -
* Run `start_cli.py` on rpi
