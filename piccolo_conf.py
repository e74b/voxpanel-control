from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine
from piccolo.engine.sqlite import SQLiteEngine
from config import POSTGRES_URL, ENV, Env
import logging

if ENV == Env.TEST:
    logging.getLogger("db").info("test environment detected: using sqlite")
    DB = SQLiteEngine()
else:
    DB = PostgresEngine(config={"dsn": POSTGRES_URL})

# A list of paths to piccolo apps
# e.g. ['blog.piccolo_app']
APP_REGISTRY = AppRegistry(apps=["users.piccolo_app"])
