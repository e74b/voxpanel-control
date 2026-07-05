from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine
from config import POSTGRES_URL

DB = PostgresEngine(config={
    "dsn": POSTGRES_URL
    })


# A list of paths to piccolo apps
# e.g. ['blog.piccolo_app']
APP_REGISTRY = AppRegistry(apps=[])
