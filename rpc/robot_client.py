import sys
from robot_pb2_grpc import RobotStub
from robot_pb2 import ActionRequest, MessageRequest
import grpc

class RobotClient():
    def __init__(self, channel):
        self.channel = channel

    def perform_action(self, actions):
        with grpc.insecure_channel(self.channel) as channel:
            stub = RobotStub(channel)
            response = stub.PerformAction(ActionRequest(actions=actions))
            print(response.reply)
            return response.reply
    
    def say_message(self, message):
        with grpc.insecure_channel(self.channel) as channel:
            stub = RobotStub(channel)
            response = stub.SayMessage(MessageRequest(message=message))
            print(response.reply)
            return response.reply

