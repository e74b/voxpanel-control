import aio_pika
from aio_pika.abc import AbstractConnection, ExchangeType, AbstractIncomingMessage
from asyncio import Queue, QueueShutDown
from config import RABBITMQ_URL, CONTROL_EXCHANGE, AGENT_PRIVATE
import logging
import json
import packets
import asyncio
from typing import Callable
from . import auth
from .exceptions import AgentNotExist, InvalidToken

class ControlNetworkHandler():

    connection: AbstractConnection
    process_queue: Queue 
    HANDLER_LUT = {}

    def __init__(self):
        self.process_queue = Queue()
        self.register_packet_handler(packets.LoginRequest, self._login)
        # queue is used here to prevent concurrency issues and avoid
        # requiring a ton of locks
        # allows each instance to be an independant instance
        # eg: 4 instances of the class can be run on 4 different threads without interfering
        # each instance will be treated like an independant control agent
    
    def register_packet_handler(self, packet: packets.BasePacket, handler: Callable[packets.BasePacket, None]):
        self.HANDLER_LUT[packet] = handler

    async def setup(self):
        self.logger = logging.getLogger("control")
        self.connection = await aio_pika.connect_robust(RABBITMQ_URL)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
                CONTROL_EXCHANGE,
                ExchangeType.TOPIC,
                arguments={
                    "x-message-ttl": 15_000
                    }
                )

        self.rpc_queue = await self.channel.declare_queue(exclusive=True)
        await self.rpc_queue.bind(self.exchange, AGENT_PRIVATE)
        await self.rpc_queue.bind(self.exchange, self.rpc_queue.name)
        await self.rpc_queue.consume(self._on_message)

    def _objectify(self, body: bytes):
        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            raise ValueError(f"invalid packet with non-json formatted text")
        except UnicodeDecodeError:
            raise ValueError(f"received packet with invalid encoding")

        
        request_type = request.pop("Type", None)
        if request_type is None:
            raise ValueError("invalid packet with missing type field")
        # i have a problem, i know

        response_class = packets.PACKET_LUT.get(request_type, None)

        if response_class is None:
            raise ValueError("received valid packet of unknown type, discarding.")

        if not issubclass(response_class, packets.BasePacket):
            # this is a server error, not an input one
            raise RuntimeError("received invalid response class packet, this is a bug")

        try:
            return response_class(**request)
        except TypeError:
            raise ValueError("received packet with missing fields")

    async def _on_message(self, message: AbstractIncomingMessage):

        try:
            packet = self._objectify(message.body)
        except ValueError as e:
            formatted_msg = "; ".join(e.args)
            self.logger.warning(formatted_msg)
            return

        try:
            await self.process_queue.put(packet)
            await message.ack()
        except QueueShutDown:
            await message.nack()

        # could do packet processing here, but its added to a queue to prevent
        # threading issues and needing a ton of locks

    async def worker_start(self):
        while True:
            packet = await self.process_queue.get()
            await self.HANDLER_LUT[type(packet)](packet)

    async def worker_stop(self):
        self.process_queue.shutdown()
        # TODO: implement console warning and timeouts
        await self.process_queue.join()

    async def _login(self, packet: packets.LoginRequest):
        self.logger.warning(f"login attempt by {packet.Uuid} {packet.Token}")
        reply_to = packet.Queue

        queue = await self.channel.get_queue(reply_to)
        await queue.bind(self.exchange, reply_to)
        try:
            meta = await auth.authenticate_agent(packet.Uuid, packet.Token)
            auth_success = True 
        except (InvalidToken, AgentNotExist):
            await queue.unbind(self.exchange, reply_to)
            auth_success = False

        response = packets.LoginResponse(
                Success=auth_success,
                Name=meta.name if auth_success else ""
                )
        raw = packets.jsonify(response)
        message = aio_pika.Message(raw.encode())
        await self.exchange.publish(message, reply_to)

        if not auth_success:
            return

