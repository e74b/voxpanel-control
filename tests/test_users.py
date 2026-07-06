import pytest
import users
from users.tables import User
from asyncpg.exceptions import UniqueViolationError

@pytest.mark.asyncio
async def test_user_signup():
    await users.create_new_user("test_username", "test_password")

    assert await User.exists().where(User.username == "test_username")

    with pytest.raises(UniqueViolationError):
        await users.create_new_user("test_username", "test_password")

