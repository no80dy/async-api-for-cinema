from typing import Optional, List

from pydantic import BaseModel, validator, Field

from models.base import BaseModelOrjson
from models.genre import Genres


class IdName(BaseModel):
    id: str
    full_name: str = Field(..., validation_alias='name')


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
