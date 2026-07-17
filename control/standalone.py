import sys
sys.path.append("control")
from .networking import ControlNetworkHandler
import asyncio
import logging

handler = ControlNetworkHandler()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ControlBootstrap")

async def main():
    await handler.setup()
    logger.info("setup complete, starting worker")
    await handler.worker_start()

asyncio.run(main())
