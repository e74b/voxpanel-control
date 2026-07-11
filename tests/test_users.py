import pytest
import users
from users.tables import User, Scope
from users.exceptions import UserNotExists, InvalidPassword, UserExists
import config


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


@pytest.mark.asyncio
async def test_user_grant_scope():
    scopes_to_grant = ["test:scope1", "test:scope2", "test:scope3"]

    await users.grant_scopes("test_username", scopes_to_grant)

    query = await Scope.select(Scope.scope).where(
        Scope.user.username == "test_username"
    )
    scopes = [record["scope"] for record in query]

    assert set(scopes).issuperset(set(scopes_to_grant))

    with pytest.raises(UserNotExists):
        await users.grant_scopes("test_username_123213", scopes_to_grant)


@pytest.mark.asyncio
async def test_user_revoke_scope():
    scopes_to_revoke = ["test:scope1", "test:scope2", "test:scope4"]
    revoked = await users.revoke_scope("test_username", scopes_to_revoke)

    if "test:scope4" in revoked:
        raise ValueError("deleted scope that should exist???")

    assert set(["test:scope1", "test:scope2"]) == set(revoked)
    with pytest.raises(UserNotExists):
        await users.revoke_scope("test_username_123213", scopes_to_revoke)

@pytest.mark.asyncio
async def test_user_get_scopes():
    scopes = await users.get_scopes("test_username")
    assert set(scopes) == set(["test:scope3", *config.DEFAULT_USER_SCOPES])

    with pytest.raises(UserNotExists):
        await users.get_scopes("test_username_123213")
