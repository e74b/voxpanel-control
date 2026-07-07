from piccolo.apps.migrations.auto.migration_manager import MigrationManager

ID = "2026-07-07T13:18:46:748076"
VERSION = "1.35.0"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="users", description=DESCRIPTION
    )

    manager.rename_table(
        old_class_name="User",
        old_tablename="user",
        new_class_name="User",
        new_tablename="vp_user",
        schema=None,
    )

    return manager
