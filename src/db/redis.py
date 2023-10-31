import abc

from redis.asyncio import Redis


cache: Redis | None = None


class Cache(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    async def get_cache(self):
        pass

    @abc.abstractmethod
    def close(self):
        pass


class Redis(Cache):
    def __init__(self, host, port):
        self.instance = Redis(host=host, port=port)

    async def get_cache(self) -> Redis:
        return self.instance

    def close(self):
        self.instance.close()


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return cache
