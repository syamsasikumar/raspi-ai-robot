from rpc.robot_pb2_grpc import RobotServicer, add_RobotServicer_to_server
from rpc.robot_pb2 import RobotReply
from concurrent import futures
import grpc
from robot_hat import Music,TTS
from robot import RobotMovement, RobotSoundOut

class RobotServer(RobotServicer):
    def __init__(self):
        music = Music()
        tts = TTS()
        self.robot_movement = RobotMovement()
        self.robot_sound_out = RobotSoundOut(music, tts)
    
    def PerformAction(self, request, context):
        actions = request.actions
        for action in actions:
            # todo
            print("performing action.." + action)
            if action == "move forward":
                self.robot_movement.forward()
            elif action == "move backward":
                self.robot_movement.backward()
            elif action == "turn left":
                self.robot_movement.left()
            elif action == "turn right":
                self.robot_movement.right()
            elif action == "play music":
                self.robot_sound_out.play_music()
            elif action == "stop music":
                self.robot_sound_out.stop_music()
            elif action == "honk":
                self.robot_sound_out.play_sound_effect()
        return RobotReply(reply="action performed")

    def SayMessage(self, request, context):
        message = ''.join(request.message)
        self.robot_sound_out.speak(message)
        # todo
        return RobotReply(reply="message spoken")
    
if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    robot_server = RobotServer()
    add_RobotServicer_to_server(robot_server, server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    server.wait_for_termination() 