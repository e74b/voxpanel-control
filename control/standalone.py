import sys
sys.path.append("control")
from .networking import ControlNetworkHandler
import packets
import asyncio
import logging
from .login import (handle_login)

handler = ControlNetworkHandler()
handler.register_packet_handler("login", packets.LoginRequest, handle_login)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ControlBootstrap")

async def main():
    await handler.setup()
    logger.info("setup complete, starting worker")
    await handler.worker_start()

asyncio.run(main())
