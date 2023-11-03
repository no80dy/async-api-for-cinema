from elasticsearch import AsyncElasticsearch


class ElasticStorage:
    def __init__(self, hosts: list[str]):
        self.instance = AsyncElasticsearch(hosts=hosts)

    async def close(self):
        await self.instance.close()
