import dotenv
import logging
import os
import sys

dotenv.load_dotenv()

logger = logging.getLogger("config")

# not configurable via .env
CONTROL_EXCHANGE = "control"
AGENT_GLOBAL = "agent-global"
AGENT_PRIVATE = "agent-private"

if "RABBITMQ_URL" not in os.environ:
    logger.error("no `RABBITMQ_URL` environment variable")
    sys.exit(1)

RABBITMQ_URL = os.environ["RABBITMQ_URL"]

