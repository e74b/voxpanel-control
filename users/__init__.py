from .tables import User, Scope
from pwdlib import PasswordHash
from asyncpg.exceptions import UniqueViolationError
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
    except UniqueViolationError:
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


def grant_scope(): ...
def revoke_scope(): ...
def get_scopes(): ...
