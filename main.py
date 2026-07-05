from aio_pika import connect_robust, ExchangeType, abc, Message
from dataclasses import dataclass, asdict
import asyncio
import logging
import json
import uuid
import time
from config import (
        RABBITMQ_URL,
        CONTROL_EXCHANGE,
        AGENT_GLOBAL,
        AGENT_PRIVATE,
        PING_TIMEOUT,
        PING_INTERVAL,
        AGENT_OFFLINE_TIMEOUT
        )
from piccolo.engine import engine_finder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("control")

@dataclass()
class LoginRequest:
    Token: str
    Queue: str

@dataclass()
class LoginResponse:
    Success: bool
    Name: str

@dataclass()
class Agent:
    name: str
    last_ping: int
    routing_key: str

class OpenRequest():
    async def resolve(): ...

class PingRequest(OpenRequest):
    def __init__(self, queue: asyncio.Queue, token: str):
        self.queue = queue
        self.token = token

    async def resolve(self, _: str, uuid: str):
        state.agents[self.token].last_ping = time.monotonic()
        try:
            await self.queue.put({"token": self.token})
        except asyncio.QueueShutDown:
            # just barely missed the timeout, next ping cycle will catch this
            return
        await state.close_request(uuid)


class DaemonState:
    agents: dict[str, Agent]
    reply_name: str
    open_requests: dict
    connection: abc.AbstractRobustConnection
    init_done: asyncio.Event

    def __init__(self):
        self.agents = {}
        self.open_requests = {}
        self.init_done = asyncio.Event()

    async def submit_request(self, uuid: str, request: OpenRequest):
        self.open_requests[uuid] = request

    async def close_request(self, uuid: str):
        self.open_requests.pop(uuid)

state = DaemonState()

async def healthcheck():
    channel = await state.connection.channel()
    exchange = await channel.declare_exchange(CONTROL_EXCHANGE, ExchangeType.TOPIC)
    ping_payload = json.dumps({"Type": "ping"}).encode()
    uuid_map = {}

    response_queue = asyncio.Queue()

    to_check = dict(state.agents)
    for token, agent in to_check.items():
        correlation_id = uuid.uuid4().hex
        ping_message = Message(
                ping_payload,
                reply_to=state.reply_name,
                correlation_id=correlation_id
                )
        uuid_map[token] = correlation_id
        await exchange.publish(ping_message, agent.routing_key)
        await state.submit_request(correlation_id, PingRequest(response_queue, token))

    await asyncio.sleep(PING_TIMEOUT)
    response_queue.shutdown(immediate=False)
    while True:
        try:
            message = await response_queue.get()
        except asyncio.QueueShutDown:
            break
        to_check.pop(message["token"])

    for token, agent in to_check.items():
        await state.close_request(uuid_map[token])
        time_s = time.monotonic() - agent.last_ping
        logger.warning(f"agent `{agent.name}` missed ping. last ping was {time_s:.2f}s ago")
        if time_s > AGENT_OFFLINE_TIMEOUT:
            logger.info(f"agent {agent.name} is now considered to be offline")
            state.agents.pop(token)
            # TODO: notify control nodes to rebuild their responsibilities and resource pool

    await channel.close()

async def healthcheck_task():
    await state.init_done.wait()
    while True:
        await asyncio.sleep(PING_INTERVAL)
        await healthcheck()

async def handle_login(message: abc.AbstractIncomingMessage, body: dict):
    data = LoginRequest(**body)
    logger.info(f"agent `Agent Name` with token `{data.Token}` has logged in")
    await message.channel.queue_bind(data.Queue, CONTROL_EXCHANGE, routing_key=data.Queue)

    # dummy ok response, will integrate with auth
    response = LoginResponse(Success=True, Name="Agent Name")
    response_raw = json.dumps(asdict(response)).encode()
    await message.channel.basic_publish(response_raw, routing_key=data.Queue)

    agent = Agent(name="Agent Name", last_ping=time.monotonic(), routing_key=data.Queue)
    state.agents[data.Token] = agent

async def on_message(message: abc.AbstractIncomingMessage):
    await message.ack()
    body_text = message.body.decode()
    try:
        body: dict = json.loads(body_text)
        if type(body) is not dict: raise ValueError()
        request = body["Type"]
        body.pop("Type")
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.warning(f"received malformed reqest from `{message.consumer_tag}`")
        return
    if not (request == "response"):
        # theres a lotta these, no need to log
        logger.info(f"received rpc request `{request}`")

    if request == "login":
        await handle_login(message, body)
    elif request == "ping":
        logger.info(f"ping corresponding to {message.correlation_id} received")
    elif request == "response":
        if message.correlation_id not in state.open_requests:
            logger.message("received unknown response uuid, ignoring")
            return

        await state.open_requests[message.correlation_id].resolve(body, message.correlation_id)

async def test_db_connect():
    engine = engine_finder()
    # TODO: Add schema tests, etc.
    await engine.start_connection_pool()
    await engine.close_connection_pool()

async def main():
    await test_db_connect()
    state.connection = await connect_robust(RABBITMQ_URL)
    channel = await state.connection.channel()
    control_exc = await channel.declare_exchange(CONTROL_EXCHANGE, ExchangeType.TOPIC, arguments={
        "x-message-ttl": 15_000,
        })
    queue = await channel.declare_queue(durable=False, exclusive=True)
    await queue.bind(control_exc, AGENT_PRIVATE)
    await queue.bind(control_exc, queue.name)
    state.reply_name = queue.name
    await queue.consume(on_message)
    state.init_done.set()
    logging.info("setup done. waiting for reqests")


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(main())
loop.create_task(healthcheck_task())
loop.run_forever()
