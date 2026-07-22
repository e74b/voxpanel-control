import time
from aio_pika import Message
from . import packets
from .networking import ControlNetworkHandler
from .exceptions import AgentNotExist, InvalidToken
from . import auth
from .networking import ConnectedAgentPeer

async def handle_login(controller: ControlNetworkHandler, packet: packets.LoginRequest):
    controller.logger.warning(f"login attempt by {packet.Uuid} {packet.Token}")
    reply_to = packet.Queue

    queue = await controller.channel.get_queue(reply_to)
    await queue.bind(controller.exchange, reply_to)
    try:
        meta = await auth.authenticate_agent(packet.Uuid, packet.Token)
        auth_success = True
        await controller.peer_lock.acquire()
        controller.peers[packet.Uuid] = ConnectedAgentPeer(
                uuid=packet.Uuid,
                name=meta.name,
                last_ping=time.monotonic(),
                queue=queue.name
                )
        controller.peer_lock.release()

    except (InvalidToken, AgentNotExist):
        await queue.unbind(controller.exchange, reply_to)
        auth_success = False

    response = packets.LoginResponse(
            Success=auth_success,
            Name=meta.name if auth_success else ""
            )
    raw = packets.jsonify(response)
    message = Message(raw)
    await controller.exchange.publish(message, reply_to)

