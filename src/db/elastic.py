from abc import ABC, abstractmethod
from elasticsearch import AsyncElasticsearch, NotFoundError


class IStorage(ABC):
    @abstractmethod
    async def get_by_id(self, scheme: str, id: str) -> dict | None:
        pass

    @abstractmethod
    async def search(self, scheme: str, query: str) -> list[dict] | None:
        pass


class ElasticStorage(IStorage):
    def __init__(self, **kwargs) -> None:
        self.connection = AsyncElasticsearch(**kwargs)

    async def get_by_id(self, index: str, id: str) -> dict | None:
        try:
            doc = await self.connection.get(index=index, id=id)
        except NotFoundError:
            return None
        return doc['_source']

    async def search(self, index: str, body: str) -> list[dict] | None:
        try:
            docs = await self.connection.search(
                index=index, body=body
            )
        except NotFoundError:
            return []
        return [doc['_source'] for doc in docs['hits']['hits']]
