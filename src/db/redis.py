from typing import Any, Coroutine

from redis.asyncio import Redis

from db.cache import Cache


class RedisCache(Cache):
    def __init__(self, host, port):
        self.instance = Redis(host=host, port=port)

    def get(self, data) -> Coroutine[Any, Any, str | bytes | None | Any]:
        return self.instance.get(data)

    def set(self, key, value, ttl):
        return self.instance.set(str(key), value, ttl)

    def close(self):
        self.instance.close()

