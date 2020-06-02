import uuid

from app.common import config
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository


async def check_username_is_taken(repo: UsersRepository, username: str) -> bool:
    try:
        await repo.get_user_by_username(username=username)
    except EntityDoesNotExist:
        return False

    return True


async def check_device_shared_token(token: str) -> bool:
    return token == config.SHARED_TOKEN


# TODO: save into database
_tokens = {}


async def generate_new_device() -> str:
    device_uid = uuid.uuid4()
    token = str(uuid.uuid4())
    _tokens[device_uid] = token
    return token


async def get_device_uid_by_token(token: str) -> uuid.UUID:
    for d_uid, d_token in _tokens.items():
        if d_token == token:
            return d_uid
    raise KeyError("device with current token not found")
