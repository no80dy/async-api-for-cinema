from redis.asyncio import Redis

from db.cache import Cache


class RedisCache(Cache):
    def __init__(self, host, port):
        self.instance = Redis(host=host, port=port)

    def get_instance(self) -> Redis:
        return self.instance

    def close(self):
        self.instance.close()

