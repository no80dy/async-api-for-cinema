from functools import lru_cache
from typing import Optional, List

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Genres


class GenreService:
    def __init__(
        self,
        redis: Redis,
        elastic: AsyncElasticsearch
    ) -> None:
        self.redis = redis
        self.elastic = elastic

    async def get_genre_by_id(
        self,
        genre_id: str
    ) -> Optional[Genres]:
        genre = await self._get_genre_by_id_from_elastic(genre_id)

        if not genre:
            return None
        return genre

    async def get_genres(self) -> List[Genres]:
        genres = await self._get_genres_from_elastic()

        if not genres:
            return []
        return genres

    async def _get_genres_from_elastic(self) -> List[Genres]:
        query = {
            'query': {
                'match_all': {}
            }
        }

        try:
            docs = await self.elastic.search(index='genres', body=query)
        except NotFoundError:
            return []
        return [Genres(**doc['_source']) for doc in docs['hits']['hits']]

    async def _get_genre_by_id_from_elastic(
        self,
        genre_id: str
    ) -> Optional[Genres]:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        return Genres(**doc['_source'])


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
