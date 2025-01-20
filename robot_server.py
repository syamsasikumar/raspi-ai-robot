from rpc.robot_pb2_grpc import RobotServicer, add_RobotServicer_to_server
from rpc.robot_pb2 import RobotReply
from concurrent import futures
import grpc

class RobotServer(RobotServicer):
    def __init__(self):
        pass
    
    def PerformAction(self, request, context):
        actions = request.actions
        for action in actions:
            # todo
            print("performing action.." + action)
        return RobotReply(reply="action performed")

    def SayMessage(self, request, context):
        message = request.message
        print(''.join(message))
        # todo
        return RobotReply(reply="message spoken")
    
if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    robot_server = RobotServer()
    add_RobotServicer_to_server(robot_server, server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    server.wait_for_termination() 