from dataclasses import dataclass, asdict
import json
from aio_pika.abc import AbstractIncomingMessage

class BasePacket:
    ...

def jsonify(packet: BasePacket):
    return json.dumps(asdict(packet)).encode()

@dataclass()
class LoginRequest(BasePacket):
    Uuid: str
    Token: str
    Queue: str

@dataclass()
class LoginResponse(BasePacket):
    Success: bool
    Name: str

@dataclass()
class HealthCheck(BasePacket):
    Time: float
    Type: str = "ping"

@dataclass()
class HealthCheckResponse(BasePacket):
    Type: str = "ping_response"
