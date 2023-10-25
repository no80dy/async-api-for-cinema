import uuid
from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonService:
    """Класс PersonService содержит бизнес-логику по работе с персонами."""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_person_by_id(self, person_id: uuid.UUID) -> Optional[Person]:
        """Функция возвращает объект персоны. Он опционален, так как персона может отсутствовать в базе."""
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def _get_person_from_elastic(self, person_id: uuid.UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index='persons', id=str(person_id))
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _person_from_cache(self, person_id: uuid.UUID) -> Optional[Person]:
        data = await self.redis.get(str(person_id))
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        person = Person.model_validate_json(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        """Сохраняем данные о персоне в кеше, время жизни кеша — 5 минут."""
        await self.redis.set(str(person.id), person.model_dump_json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_persons_by_query(self,
                                   query: str,
                                   page_size: int,
                                   page_number: int
                                   ) -> Optional[list[Person]]:
        """Функция возвращает список персон на основании запроса."""
        persons = await self._get_persons_by_query_from_elastic(
            query, page_size, page_number
        )

        if not persons:
            return []
        return persons

    async def _get_persons_by_query_from_elastic(self,
                                                 query: str,
                                                 page_size: int,
                                                 page_number: int
                                                 ) -> Optional[list[Person]]:
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
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
