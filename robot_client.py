from rpc.robot_pb2_grpc import RobotStub
from rpc.robot_pb2 import ActionRequest, MessageRequest
from dotenv import load_dotenv
import grpc
import os

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

if __name__ == "__main__":
    load_dotenv()
    rpc_channel = os.getenv("RPC_CHANNEL")
    print(rpc_channel)
    robot_client = RobotClient(rpc_channel)
    robot_client.say_message("Hello there! Beep boop! Im Max, the little robot ready to roll into action! How can I assist you today?")