import dotenv
import logging
import os
import sys
from typing import NewType

dotenv.load_dotenv()

logger = logging.getLogger("config")

TimeSecond = NewType("TimeSecond", int)
# not configurable via .env
CONTROL_EXCHANGE = "control"
AGENT_GLOBAL = "agent-global"
AGENT_PRIVATE = "agent-private"
DEFAULT_USER_SCOPES = ["user:test"]

# time between pings
PING_INTERVAL: TimeSecond = 12

# time to wait after ping emit, for responses
PING_TIMEOUT: TimeSecond = 3

# time after last ping, after which agent will be considered offline
AGENT_OFFLINE_TIMEOUT: TimeSecond = 60

if "RABBITMQ_URL" not in os.environ:
    logger.error("no `RABBITMQ_URL` environment variable")
    sys.exit(1)

RABBITMQ_URL = os.environ["RABBITMQ_URL"]

if "POSTGRES_URL" not in os.environ:
    logger.error("no `POSTGRES_URL` environment variable")

POSTGRES_URL = os.environ["POSTGRES_URL"]


class Env:
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


ENV = os.environ.get("ENV", Env.DEV)
