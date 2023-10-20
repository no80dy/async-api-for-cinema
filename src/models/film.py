from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List

import orjson
from pydantic import BaseModel, Field, validator


def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


def datetime_now() -> datetime:
    return datetime.now(timezone.utc)


class BaseModelOrjson(BaseModel):
    id: str = Field(..., alias='uuid')
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_field_name = True


class IdName(BaseModel):
    id: str
    full_name: str


class TypeChoices(str, Enum):
    MOVIE = 'MOVIE'
    TV_SHOW = 'TV_SHOW'


class FilmShort(BaseModelOrjson):
    """
    Схемы ответов для:
    /api/v1/films
    /api/v1/films/search/
    /api/v1/persons/<uuid:UUID>/film/
    """
    title: str
    imdb_rating: Optional[float]

    @validator('imdb_rating')
    def check_rating(cls, rating):
        if rating > 100 or rating < 0:
            raise ValueError('Ошибка валидации рейтинга')
        return rating


class Genres(BaseModelOrjson):
    """
    Схемы ответов для:
    /api/v1/genres/
    /api/v1/genres/<uuid:UUID>/
    """
    name: str


class PersonRoles(BaseModelOrjson):
    roles: Optional[List[str]]


class Persons(BaseModelOrjson):
    """
    Схемы ответов для:
    /api/v1/persons/search/
    /api/v1/persons/<uuid:UUID>/
    """
    full_name: str
    films: Optional[List[PersonRoles]]


class Film(FilmShort):
    """
    Схемы ответов для:
    /api/v1/films/<uuid:UUID>/
    """
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genres: List[Genres]
    actors: List[IdName]
    writers: List[IdName]
    directors: List[IdName]
