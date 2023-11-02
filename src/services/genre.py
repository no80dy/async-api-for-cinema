import json
from functools import lru_cache
from typing import Any
from uuid import UUID

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.cache import Cache, get_cache
from db.elastic import get_elastic
from models.genre import Genres

GENRE_CACHE_EXPIRE_IN_SECONDS = 5 * 60  # 5 min


class GenreService:
    """Класс GenreService содержит бизнес-логику по работе с жанрами."""

    def __init__(
        self,
        cache: Cache,
        elastic: AsyncElasticsearch
    ) -> None:
        self.cache = cache
        self.elastic = elastic

    async def get_genre_by_id(
        self,
        genre_id: UUID
    ) -> Genres | None:
        genre = await self._genre_from_cache(str(genre_id))
        if not genre:
            genre = await self._get_genre_by_id_from_elastic(genre_id)

            if not genre:
                return None

            await self._put_genre_to_cache(genre.json(), str(genre_id))
        return genre

    async def get_genres(self) -> list[Genres]:
        genres = await self._genre_from_cache('genres')
        if not genres:
            genres = await self._get_genres_from_elastic()

            if not genres:
                return []
            value = json.dumps([genre.json() for genre in genres])
            await self._put_genre_to_cache(value, 'genres')

        return genres

    async def _get_genres_from_elastic(self) -> list[Genres]:
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
    ) -> Genres | None:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        return Genres(**doc['_source'])

    async def _genre_from_cache(
        self,
        key: str
    ) -> None | Genres | list[Genres]:
        data = await self.cache.get(key)
        if not data:
            return None
        if key == 'genres':
            return [Genres.parse_raw(obj) for obj in json.loads(data)]
        return Genres.parse_raw(data)

    async def _put_genre_to_cache(self, value: Any, key: str):
        await self.cache.set(
            str(key), value, GENRE_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_genre_service(
    cache: Cache = Depends(get_cache),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(cache, elastic)
