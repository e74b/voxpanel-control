from dataclasses import dataclass


class BasePacket:
    ...

@dataclass(BasePacket)
class LoginRequest:
    Uuid: str
    Token: str
    Queue: str


PACKET_LUT = {
        "login": LoginRequest
        }
