from uuid import UUID
from functools import lru_cache
from typing import Optional, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from models.person import Person

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_film_by_id(self, film_id: UUID) -> Optional[Film]:
        film = await self._get_film_from_elastic(film_id)
        if not film:
            return None

        return film

    async def get_films_by_query(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> List[Film]:
        films = await self._get_films_by_query_from_elastic(
            query, page_size, page_number
        )

        if not films:
            return []
        return films

    async def get_films_with_sort(
        self,
        sort: str,
        page_size: int,
        page_number: int
    ) -> List[Film]:
        films = await self._get_films_with_sort_from_elastic(
            sort, page_size, page_number
        )

        if not films:
            return []
        return films

    async def get_films_by_genre_id_with_sort(
        self,
        genre_id: UUID,
        sort: str,
        page_size: int,
        page_number: int
    ) -> List[Film]:
        films = await self._get_films_by_genre_id_with_sort_from_elastic(
            genre_id, sort, page_size, page_number
        )

        if not films:
            return []
        return films

    async def _get_films_by_genre_id_with_sort_from_elastic(
        self,
        genre_id: UUID,
        sort: str,
        page_size: int,
        page_number: int
    ) -> List[Film]:
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
        return [Film(**doc['_source']) for doc in docs['hits']['hits']]

    async def _get_films_by_query_from_elastic(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> List[Film]:
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
        return [Film(**doc['_source']) for doc in docs['hits']['hits']]

    async def _get_films_with_sort_from_elastic(
        self,
        sort: str,
        page_size: int,
        page_number: int
    ) -> List[Film]:
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
        return [Film(**doc['_source']) for doc in docs['hits']['hits']]

    async def get_person_films(
        self,
        person: Person,
    ) -> List[Film]:

        film_ids = [str(film.id) for film in person.films]

        person_films = await self._get_films_by_ids_from_elastic(film_ids)

        if not person_films:
            return []
        return person_films

    async def _get_films_by_ids_from_elastic(
            self,
            film_ids: list[str],
    ) -> List[Film]:

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

        print(docs)
        return [Film(**doc['_source']) for doc in docs['hits']['hits']]

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(
            film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS
        )

    def _calculate_offset(self, page_size: int, page_number: int) -> int:
        return (page_number - 1) * page_size

    def _get_sort_field(self, sort: str) -> str:
        return sort[1:] if sort.startswith('-') else sort

    def _get_sort_order(self, sort: str) -> str:
        return 'desc' if sort.startswith('-') else 'asc'


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
