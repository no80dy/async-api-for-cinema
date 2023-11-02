import abc

from redis.asyncio import Redis

cache: Redis | None = None


class Cache(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    async def get_instance(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass


# Функция понадобится при внедрении зависимостей
async def get_cache() -> Redis:
    return cache
