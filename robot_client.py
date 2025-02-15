from rpc.robot_pb2_grpc import RobotStub
from rpc.robot_pb2 import ActionRequest, MessageRequest
import grpc
import os
from dotenv import load_dotenv


def get_rpc_channel():
    load_dotenv()
    if os.getenv("RPC_SERVER_MODE") == "local":
        return os.getenv("RPC_LOCAL_CHANNEL")
    return os.getenv("RPC_CHANNEL")


class RobotClient:
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
    rpc_channel = get_rpc_channel()
    print(rpc_channel)
    robot_client = RobotClient(rpc_channel)
    robot_client.perform_action(["free_roam"])
    robot_client.say_message(
        "Hello there! Beep boop! Im Max, the little robot ready to roll into action! How can I assist you today?"
    )
