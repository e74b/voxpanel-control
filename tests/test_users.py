import pytest
import users
from users.tables import User
from users.exceptions import UserNotExists, InvalidPassword, UserExists

@pytest.mark.asyncio
async def test_user_signup():
    await users.create_new_user("test_username", "test_password")

    assert await User.exists().where(User.username == "test_username")

    with pytest.raises(UserExists):
        await users.create_new_user("test_username", "test_password")

@pytest.mark.asyncio
async def test_user_login():
    granted_scopes = await users.authenticate_user("test_username", "test_password")
    assert isinstance(granted_scopes, list)

    with pytest.raises(UserNotExists):
        await users.authenticate_user("test_username_123213", "test_password")
    with pytest.raises(InvalidPassword):
        await users.authenticate_user("test_username", "notthepassword")
