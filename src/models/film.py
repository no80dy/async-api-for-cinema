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
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime = Field(default_factory=datetime_now)
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_field_name = True


class IdName(BaseModel):
    id: str
    name: str


class TypeChoices(str, Enum):
    MOVIE = 'MOVIE'
    TV_SHOW = 'TV_SHOW'


class FilmShort(BaseModelOrjson):
    title: str
    description: str


class Film(BaseModelOrjson):
    rating: Optional[float]
    title: str
    description: Optional[str]
    creation_date: Optional[datetime]
    type: TypeChoices
    # аннотированные поля
    actors: List[IdName]
    writers: List[IdName]
    directors: List[IdName]
    genres: List[IdName]

    @validator('rating')
    def check_rating(cls, rating):
        if rating > 100 or rating < 0:
            raise ValueError('Ошибка валидации рейтинга')
        return rating


class Genre(BaseModelOrjson):
    name: str
    description: str
    films: List[FilmShort]


class Person(BaseModelOrjson):
    full_name: str
    # ниже данные из таблицы PersonFilmWork
    roles: List[str]
    film_ids: List[str]
