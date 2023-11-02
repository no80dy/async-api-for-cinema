import json
import uuid
from functools import lru_cache
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.cache import Cache, get_cache
from db.elastic import get_elastic
from db.storage import BaseStorage
from models.person import Person


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    """Класс PersonService содержит бизнес-логику по работе с персонами."""

    def __init__(self, cache: Cache, elastic: AsyncElasticsearch):
        self.cache = cache
        self.elastic = elastic

    async def get_person_by_id(self, person_id: uuid.UUID) -> Person | None:
        """
        Функция возвращает объект персоны.
        Он опционален, так как персона может отсутствовать в базе.
        """
        person = await self._person_from_cache(str(person_id))
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(
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
        persons = await self._person_from_cache(key)
        if not persons:
            persons = await self._get_persons_by_query_from_elastic(
                query, page_size, page_number
            )

            if not persons:
                return []
            value = json.dumps(
                [person.model_dump_json() for person in persons]
            )
            await self._put_person_to_cache(value, key)

        return persons

    async def _get_person_from_elastic(
        self,
        person_id: uuid.UUID
    ) -> Person | None:
        try:
            doc = await self.elastic.get(index='persons', id=str(person_id))
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _person_from_cache(
        self,
        key: str
    ) -> None | Person | list[Person] | Any:
        data = await self.cache.get_instance().get(key)
        if not data:
            return None

        if '/' not in key:
            # pydantic предоставляет удобное API для создания
            # объекта моделей из json
            return Person.model_validate_json(data)
        return [Person.model_validate_json(obj) for obj in json.loads(data)]

    async def _put_person_to_cache(self, value: Any, key: str):
        """Сохраняем данные о персоне в кеше, время жизни кеша — 5 минут."""
        await self.cache.get_instance().set(key, value, FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _get_persons_by_query_from_elastic(
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

    def _calculate_offset(self, page_size: int, page_number: int) -> int:
        return (page_number - 1) * page_size


@lru_cache()
def get_person_service(
    cache: Cache = Depends(get_cache),
    elastic: BaseStorage = Depends(get_elastic),
) -> PersonService:
    return PersonService(cache, elastic.get_instance())
