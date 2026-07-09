from .tables import User, Scope
from pwdlib import PasswordHash
from asyncpg.exceptions import UniqueViolationError
from sqlite3 import IntegrityError
from config import DEFAULT_USER_SCOPES
from piccolo.engine import engine_finder
from .exceptions import (
        UserExists,
        UserNotExists,
        InvalidPassword
        )
hasher = PasswordHash.recommended()

async def create_new_user(username: str, password: str, scopes: list[str] | None = None) -> None:
    """
    Create a new user with default or specified scopes.

    Args:
        username: new user username
        password: unhashed, plaintext password
        scopes: optional, scopes to be granted to new user

    Returns:
        None

    Raises:
        UserExists: username taken
    """
    db = engine_finder()
    transaction = db.atomic()
    hashed_password = hasher.hash(password)
    user = User(username=username, password=hashed_password)
    transaction.add(User.insert(user))

    scope_strs =  DEFAULT_USER_SCOPES if scopes is None else scopes
    scope_objs = [
            Scope(user=user, scope=scope)
            for scope in scope_strs
            ]

    transaction.add(Scope.insert(*scope_objs))

    try:
        await transaction.run() # May raise UniqueViolationError
    except (UniqueViolationError, IntegrityError):
        raise UserExists()

async def authenticate_user(username: str, password: str) -> list[str]:
    """
    Authenticate an existing user and return all granted scopes.

    Args:
        username: username to authenticate
        password: unhashed plaintext password

    Returns:
        list[str]: granted scopes

    Raises:
        InvalidPassword: incorrect password given
        UserNotExists: username not found in database
    """

    user = await User.objects().get(User.username == username)
    if user is None:
        raise UserNotExists()
    if not hasher.verify(password, user.password):
        raise InvalidPassword()

    records = await Scope.select(Scope.scope).where(Scope.user == user)
    return [record["scope"] for record in records]


async def grant_scopes(username: str, scopes: str | list[str]):
    """
    Grant user permission to call all scope methods

    Args:
        username: username of user to grant the scope to
        scopes: the scope or scopes to be granted

    Returns:
        None

    Raises:
        UserNotExists: username does not exist
    """

    user =  await User.objects().get(User.username == username)

    if user is None:
        raise UserNotExists()
    if isinstance(scopes, str):
        scopes = [scopes]

    new_scopes = [Scope(user=user, scope=scope) for scope in scopes]
    await Scope.insert(*new_scopes)

async def revoke_scope(username: str, scopes: str | list[str]): 
    """
    Revoke user permission to call all scope methods

    If the scope or any of the provided scopes are not aldready granted,
    the function will not raise an error. 

    Args:
        username: username of user to revoke scope from
        scopes: the scope or scopes to be revoked

    Returns:
        list[str]: the scopes that were deleted

    Raises:
        UserNotExists: username
    """


    if isinstance(scopes, list):
        scopes = [scopes]
    # this is an extra db query
    # i'm not too sure how to raise an error in the second query if the user
    # is not found, it just returns empty which may also mean that no scopes
    # were deleted

    user_exists = await User.exists().where(User.username == username)
    if not user_exists:
        raise UserNotExists()

    result = await Scope.delete().where(
            Scope.user.username == username
        ).where(
            Scope.scope.is_in(*scopes)
        ).returning(Scope.scope)
    return [record["scope"] for record in result]

def get_scopes(): ...
