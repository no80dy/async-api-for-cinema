from redis.asyncio import Redis


class RedisCache:
    def __init__(self, host: str, port: int) -> None:
        self.connection = Redis(host=host, port=port)

    def get_connection(self):
        return self.connection

    async def close(self):
        await self.connection.close()
