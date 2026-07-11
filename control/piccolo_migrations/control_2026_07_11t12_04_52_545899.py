from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Text
from piccolo.columns.column_types import UUID
from piccolo.columns.defaults.uuid import UUID4
from piccolo.columns.indexes import IndexMethod

ID = "2026-07-11T12:04:52:545899"
VERSION = "1.35.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="control", description=DESCRIPTION
    )

    manager.add_table(
        class_name="Agent", tablename="agent", schema=None, columns=None
    )

    manager.add_column(
        table_class_name="Agent",
        tablename="agent",
        column_name="name",
        db_column_name="name",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Agent",
        tablename="agent",
        column_name="uuid",
        db_column_name="uuid",
        column_class_name="UUID",
        column_class=UUID,
        params={
            "default": UUID4(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Agent",
        tablename="agent",
        column_name="token",
        db_column_name="token",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    return manager
