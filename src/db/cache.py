import abc

from redis.asyncio import Redis

cache: Redis | None = None


class Cache(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    async def get(self, data):
        pass

    @abc.abstractmethod
    async def set(self, key, value, ttl):
        pass

    @abc.abstractmethod
    def close(self):
        pass


# Функция понадобится при внедрении зависимостей
async def get_cache() -> Redis:
    return cache
