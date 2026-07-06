from .tables import User, Scope
from pwdlib import PasswordHash
from asyncpg.exceptions import UniqueViolationError
from config import DEFAULT_USER_SCOPES
from piccolo.engine import engine_finder

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
        UniqueViolationError: username taken
    """
    db = engine_finder()
    transaction = db.transaction()
    hashed_password = hasher.hash(password)
    user = User(username=username, password=hashed_password)
    transaction.add(User.insert(user))

    scope_strs =  DEFAULT_USER_SCOPES if scopes is None else scopes
    scope_objs = [
            Scope(user=user, scope=scope)
            for scope in scope_strs
            ]

    transaction.add(Scope.insert(*scope_objs))

    await transaction.run() # May raise UniqueViolationError

def authenticate_user(): ...
def grant_scope(): ...
def revoke_scope(): ...
def get_scopes(): ...
