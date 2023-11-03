from elasticsearch import AsyncElasticsearch


class ElasticStorage:
    def __init__(self, hosts: list[str]):
        self.connection = AsyncElasticsearch(hosts=hosts)

    def get_connection(self):
        return self.connection

    async def close(self):
        await self.connection.close()
