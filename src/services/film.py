from functools import lru_cache
from typing import Optional, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_film_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

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

    async def _get_films_by_query_from_elastic(
        self,
        query: str,
        page_size: int,
        page_number: int
    ) -> List[Film]:
        search_query = {
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
            docs = await self.elastic.search(index='movies', body=search_query)
        except NotFoundError:
            return []
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
        await self.redis.set(film.id, film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    def _calculate_offset(page_size: int, page_number: int) -> int:
        return (page_number - 1) * page_size


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
