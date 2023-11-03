from redis.asyncio import Redis


class RedisCache:
    def __init__(self, host: str, port: int) -> None:
        self.instance = Redis(host=host, port=port)

    async def close(self):
        await self.instance.close()
