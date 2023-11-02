from db.storage import BaseStorage
from elasticsearch import AsyncElasticsearch


class ElasticStorage(BaseStorage):
    def __init__(self, hosts: list[str]) -> None:
        self.elastic = AsyncElasticsearch(hosts=hosts)

    def get_instance(self) -> AsyncElasticsearch:
        return self.elastic

    async def close_instance(self) -> None:
        await self.elastic.close()


es: ElasticStorage | None = None


async def get_elastic() -> ElasticStorage:
    return es
