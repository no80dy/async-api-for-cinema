from typing import Any
from abc import ABC, abstractmethod
from redis.asyncio import Redis


class ICache(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    async def set(self, value: Any, key: str, expired_time: int) -> None:
        pass


class RedisCache(ICache):
    def __init__(self, **kwargs) -> None:
        self.connection = Redis(**kwargs)

    async def get(self, key: str) -> str | None:
        return await self.connection.get(key)

    async def set(self, value: Any, key: str, expired_time: int) -> None:
        await self.connection.set(key, value, expired_time)
