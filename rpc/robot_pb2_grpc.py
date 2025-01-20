# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from robot_pb2 import MessageRequest, ActionRequest, RobotReply

GRPC_GENERATED_VERSION = '1.69.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in robot_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class RobotStub(object):
    """definitions for rpc calls to robot
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.PerformAction = channel.unary_unary(
                '/Robot/PerformAction',
                request_serializer=ActionRequest.SerializeToString,
                response_deserializer=RobotReply.FromString,
                _registered_method=True)
        self.SayMessage = channel.unary_unary(
                '/Robot/SayMessage',
                request_serializer=MessageRequest.SerializeToString,
                response_deserializer=RobotReply.FromString,
                _registered_method=True)


class RobotServicer(object):
    """definitions for rpc calls to robot
    """

    def PerformAction(self, request, context):
        """actions for robot to perform
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SayMessage(self, request, context):
        """message for robot to speak
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RobotServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'PerformAction': grpc.unary_unary_rpc_method_handler(
                    servicer.PerformAction,
                    request_deserializer=ActionRequest.FromString,
                    response_serializer=RobotReply.SerializeToString,
            ),
            'SayMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.SayMessage,
                    request_deserializer=MessageRequest.FromString,
                    response_serializer=RobotReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Robot', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('Robot', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Robot(object):
    """definitions for rpc calls to robot
    """

    @staticmethod
    def PerformAction(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Robot/PerformAction',
            ActionRequest.SerializeToString,
            RobotReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SayMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/Robot/SayMessage',
            MessageRequest.SerializeToString,
            RobotReply.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
