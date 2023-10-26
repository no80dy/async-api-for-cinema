import json
from uuid import UUID
from functools import lru_cache
from typing import Optional, List, Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genres


GENRE_CACHE_EXPIRE_IN_SECONDS = 5 * 60  # 5 min


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
        genre_id: UUID
    ) -> Optional[Genres]:
        genre = await self._genre_from_cache(str(genre_id))
        if not genre:
            genre = await self._get_genre_by_id_from_elastic(genre_id)

            if not genre:
                return None

            await self._put_genre_to_cache(genre.json(), str(genre_id))
        return genre

    async def get_genres(self) -> List[Genres]:
        genres = await self._genre_from_cache('genres')
        if not genres:
            genres = await self._get_genres_from_elastic()

            if not genres:
                return []
            value = json.dumps([genre.json() for genre in genres])
            await self._put_genre_to_cache(value, 'genres')

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
        genre_id: UUID
    ) -> Optional[Genres]:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        return Genres(**doc['_source'])

    async def _genre_from_cache(
        self,
        key: str
    ) -> None | Genres | list[Genres]:
        data = await self.redis.get(key)
        if not data:
            return None
        if key == 'genres':
            return [Genres.parse_raw(obj) for obj in json.loads(data)]
        return Genres.parse_raw(data)

    async def _put_genre_to_cache(self, value: Any, key: str):
        await self.redis.set(
            str(key), value, GENRE_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
