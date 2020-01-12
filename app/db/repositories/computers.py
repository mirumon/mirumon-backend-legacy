import hashlib
import pickle
from typing import Any, Hashable, Optional

import aioredis
from starlette.datastructures import URL


# TODO refactor
class RedisRepo:
    redis: aioredis.Redis
    dsn: str
    prefix: Optional[str]
    delimiter: str
    expire: Optional[int]

    def __init__(
        self, dsn: URL, prefix: Optional[str] = None, expire: Optional[int] = None
    ) -> None:
        self.dsn = str(dsn)
        self.prefix = prefix
        self.expire = expire
        self.delimiter = "_"

    @classmethod
    async def init(
        cls, dsn: URL, prefix: Optional[str] = None, expire: Optional[int] = None
    ) -> "RedisRepo":
        repo = cls(dsn=dsn, prefix=prefix, expire=expire)
        repo.redis = await aioredis.create_redis_pool(repo.dsn)

        return repo

    async def close(self) -> None:
        self.redis.close()
        await self.redis.wait_closed()

    def __key(self, arg: Hashable) -> str:
        if self.prefix is not None:
            _prefix = self.prefix + self.delimiter
        else:
            _prefix = ""

        return _prefix + hashlib.md5(pickle.dumps(arg)).hexdigest()

    async def get(self, key: Hashable, default: Any = None) -> Any:
        cached_data = await self.redis.get(self.__key(key))
        if cached_data is None:
            return default
        else:
            return pickle.loads(cached_data)

    async def set(
        self, key: Hashable, value: Any, expire: Optional[int] = None
    ) -> None:
        if expire is None:
            expire = self.expire
        await self.redis.set(self.__key(key), pickle.dumps(value), expire=expire)
