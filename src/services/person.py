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
    """Класс PersonService содержит бизнес-логику по работе с фильмами."""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: uuid.UUID) -> Optional[Person]:
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
        person = Person.model_validate_strings(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        """Сохраняем данные о персоне в кеше, время жизни кеша — 5 минут."""
        await self.redis.set(person.id, person.model_dump_json(), FILM_CACHE_EXPIRE_IN_SECONDS)


# get_person_service — это провайдер PersonService.
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Для их получения вы ранее создали функции-провайдеры в модуле db
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
