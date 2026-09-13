from functools import lru_cache

from arq import ArqRedis
from arq.connections import RedisSettings, create_pool

from src.core.config import SETTINGS


@lru_cache
def get_redis_settings() -> RedisSettings:
    return RedisSettings(
        host=SETTINGS.redis_host,
        port=SETTINGS.redis_port,
        database=SETTINGS.redis_db,
        password=SETTINGS.redis_password,
    )


class RedisManager:
    _redis_pool = None

    def __init__(
        self,
        redis_settings: RedisSettings,
    ) -> None:
        self._redis_settings = redis_settings

    async def get_pool(self) -> ArqRedis:
        if not self._redis_pool:
            self._redis_pool = await create_pool(self._redis_settings)
        return self._redis_pool


@lru_cache
def get_redis_manager() -> RedisManager:
    redis_settings = get_redis_settings()
    return RedisManager(redis_settings=redis_settings)
