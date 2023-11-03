import json
import uuid

from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any

from elasticsearch import NotFoundError
from fastapi import Depends

from db.storage import get_elastic
from db.cache import get_cache

from db.elastic import ElasticStorage
from db.redis import RedisCache

from models.person import Person


class CachePersonHandler(ABC):
    @abstractmethod
    async def get_person(key: str):
        pass

    @abstractmethod
    async def put_person(value: str, key: str):
        pass


class StoragePersonHandler(ABC):
    @abstractmethod
    async def get_persons_by_query(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> list[Person] | None:
        pass

    @abstractmethod
    async def get_person(
        self,
        person_id: uuid.UUID
    ) -> Person | None:
        pass


class RedisPersonHandler(CachePersonHandler):
    def __init__(self, cache: RedisCache, expired_time: int) -> None:
        self.cache = cache.get_connection()
        self.expired_time = expired_time

    async def get_person(self, key: str) -> None | Person | list[Person] | Any:
        data = await self.cache.get(key)
        if not data:
            return None

        if '/' not in key:
            return Person.model_validate_json(data)
        return [Person.model_validate_json(obj) for obj in json.loads(data)]

    async def put_person(self, value: Any, key: str):
        await self.cache.set(key, value, self.expired_time)


class ElasticPersonHandler(StoragePersonHandler):
    def __init__(self, elastic: ElasticStorage) -> None:
        self.elastic = elastic.get_connection()

    async def get_persons_by_query(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> list[Person] | None:
        elastic_query = {
            'query': {
                'fuzzy': {
                    'full_name': {
                        'value': query,
                        'fuzziness': 'AUTO'
                    }
                }
            },
            'size': page_size,
            'from': self._calculate_offset(page_size, page_number)
        }

        try:
            docs = await self.elastic.search(
                index='persons', body=elastic_query
            )
        except NotFoundError:
            return []
        return [Person(**doc['_source']) for doc in docs['hits']['hits']]

    async def get_person(
        self,
        person_id: uuid.UUID
    ) -> Person | None:
        try:
            doc = await self.elastic.get(index='persons', id=str(person_id))
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    def _calculate_offset(self, page_size: int, page_number: int) -> int:
        return (page_number - 1) * page_size


class PersonService:
    """Класс PersonService содержит бизнес-логику по работе с персонами."""

    def __init__(
        self,
        cache_handler: CachePersonHandler,
        storage_handler: StoragePersonHandler
    ) -> None:
        self.cache_handler = cache_handler
        self.storage_handler = storage_handler

    async def get_person_by_id(self, person_id: uuid.UUID) -> Person | None:
        """
        Функция возвращает объект персоны.
        Он опционален, так как персона может отсутствовать в базе.
        """
        person = await self.cache_handler.put_person(str(person_id))
        if not person:
            person = await self.storage_handler.get_person(person_id)
            if not person:
                return None
            await self.cache_handler.put_person(
                person.model_dump_json(), str(person_id)
            )

        return person

    async def get_persons_by_query(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> list[Person] | None:
        """Функция возвращает список персон на основании запроса."""
        key = f'{query}/{page_size}/{page_number}'
        persons = await self.cache_handler.get_person(key)
        if not persons:
            persons = await self.storage_handler.get_persons_by_query(
                query, page_size, page_number
            )

            if not persons:
                return []
            value = json.dumps(
                [person.model_dump_json() for person in persons]
            )
            await self.cache_handler.put_person(value, key)

        return persons


@lru_cache()
def get_person_service(
    cache: RedisCache = Depends(get_cache),
    elastic: ElasticStorage = Depends(get_elastic),
) -> PersonService:
    cache_handler = RedisPersonHandler(cache, 60 * 5)
    storage_handler = ElasticPersonHandler(elastic)
    return PersonService(cache_handler, storage_handler)
