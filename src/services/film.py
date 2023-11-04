import json
from functools import lru_cache
from typing import Any
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends


from db.cache import get_cache
from db.redis import ICache
from db.storage import get_elastic
from models.film import Film
from models.person import Person


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    """Класс FilmService содержит бизнес-логику по работе с фильмами."""

    def __init__(self, cache: ICache, elastic: AsyncElasticsearch):
        self.cache = cache
        self.elastic = elastic

    async def get_film_by_id(self, film_id: UUID) -> Film | None:
        film = await self._film_from_cache(str(film_id))
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(str(film_id))
            if not film:
                # Если он отсутствует в Elasticsearch,
                # значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film.json(), str(film_id))

        return film

    async def get_films_by_query(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> list[Film]:
        key = f'{query}/{page_size}/{page_number}'
        films = await self._film_from_cache(key)
        if not films:
            films = await self._get_films_by_query_from_elastic(
                query, page_size, page_number
            )
            if not films:
                return []
            value = json.dumps([film.json() for film in films])
            await self._put_film_to_cache(value, key)

        return films

    async def get_films_with_sort(
        self,
        sort: str,
        page_size: int,
        page_number: int
    ) -> list[Film]:
        key = f'{sort}/{page_size}/{page_number}'
        films = await self._film_from_cache(key)
        if not films:
            films = await self._get_films_with_sort_from_elastic(
                sort, page_size, page_number
            )
            if not films:
                return []
            value = json.dumps([film.json() for film in films])
            await self._put_film_to_cache(value, key)

        return films

    async def get_films_by_genre_id_with_sort(
        self,
        genre_id: UUID,
        sort: str,
        page_size: int,
        page_number: int
    ) -> list[Film]:
        key = f'{genre_id}/{sort}/{page_size}/{page_number}'
        films = await self._film_from_cache(key)
        if not films:
            films = await self._get_films_by_genre_id_with_sort_from_elastic(
                genre_id, sort, page_size, page_number
            )
            if not films:
                return []
            value = json.dumps([film.json() for film in films])
            await self._put_film_to_cache(value, key)

        return films

    async def get_person_films(
        self,
        person: Person,
    ) -> list[Film]:

        film_ids = [str(film.id) for film in person.films]

        key = '/'.join(film_ids)
        person_films = await self._film_from_cache(key)
        if not person_films:
            person_films = await self._get_films_by_ids_from_elastic(film_ids)
            if not person_films:
                return []
            value = json.dumps([film.json() for film in person_films])
            await self._put_film_to_cache(value, key)

        return person_films

    async def _get_films_by_genre_id_with_sort_from_elastic(
        self,
        genre_id: UUID,
        sort: str,
        page_size: int,
        page_number: int
    ) -> list[Film]:
        elastic_query = {
            'query': {
                'nested': {
                    'path': 'genres',
                    'query': {
                        'match': {
                            'genres.id': genre_id
                        }
                    }
                }
            },
            'sort': [
                {
                    self._get_sort_field(sort): {
                        'order': self._get_sort_order(sort)
                    }
                }
            ],
            'size': page_size,
            'from': self._calculate_offset(page_size, page_number)
        }

        try:
            docs = await self.elastic.search(
                index='movies', body=elastic_query
            )
        except NotFoundError:
            return []
        return [Film(**doc) for doc in docs]

    async def _get_films_by_query_from_elastic(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> list[Film]:
        elastic_query = {
            'query': {
                'fuzzy': {
                    'title': {
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
                index='movies', body=elastic_query
            )
        except NotFoundError:
            return []
        return [Film(**doc) for doc in docs]

    async def _get_films_with_sort_from_elastic(
        self,
        sort: str,
        page_size: int,
        page_number: int
    ) -> list[Film]:
        elastic_query = {
            'sort': [
                {
                    self._get_sort_field(sort): {
                        'order': self._get_sort_order(sort)
                    }
                }
            ],
            'size': page_size,
            'from': self._calculate_offset(page_size, page_number)
        }

        try:
            docs = await self.elastic.search(
                index='movies', body=elastic_query
            )
        except NotFoundError:
            return []
        return [Film(**doc) for doc in docs]

    async def _get_films_by_ids_from_elastic(
            self,
            film_ids: list[str],
    ) -> list[Film]:

        elastic_query = {
            'query': {
                'ids': {
                    'values': film_ids
                }
            }
        }

        try:
            docs = await self.elastic.search(
                index='movies', body=elastic_query
            )
        except NotFoundError:
            return []

        return [Film(**doc) for doc in docs]

    async def _get_film_from_elastic(self, film_id: str) -> Film | None:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc)

    async def _film_from_cache(self, key: str) -> None | Film | list[Film]:
        data = await self.cache.get(key)
        if not data:
            return None

        if '/' not in key:
            return Film.parse_raw(data)
        return [Film.parse_raw(obj) for obj in json.loads(data)]

    async def _put_film_to_cache(self, value: Any, key: str):
        await self.cache.set(
            str(key), value, FILM_CACHE_EXPIRE_IN_SECONDS
        )

    def _calculate_offset(self, page_size: int, page_number: int) -> int:
        return (page_number - 1) * page_size

    def _get_sort_field(self, sort: str) -> str:
        return sort[1:] if sort.startswith('-') else sort

    def _get_sort_order(self, sort: str) -> str:
        return 'desc' if sort.startswith('-') else 'asc'


@lru_cache()
def get_film_service(
    cache: ICache = Depends(get_cache),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(cache, elastic)
