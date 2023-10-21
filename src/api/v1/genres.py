from typing import List
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from services.genre import GenreService, get_genre_service
from models.film import Genres


router = APIRouter()


@router.get(
    '/{genre_id}',
    response_model=Genres,
    summary='Информация по жанру',
    description='Получение подробной информации о конкретном жанре',
    response_description='Информация по жанру'
)
async def genre_details(
    genre_id: UUID,
    genre_service: GenreService = Depends(get_genre_service)
) -> Genres:
    genre = await genre_service.get_genre_by_id(str(genre_id))

    if not genre:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found'
        )

    return genre


@router.get(
    '/',
    response_model=List[Genres],
    summary='Список всех жанров',
    description='Возвращает список всех доступных жанров',
    response_description='Список жанров'
)
async def genres(
    genre_service: GenreService = Depends(get_genre_service)
) -> List[Genres]:
    genres = await genre_service.get_genres()

    if not genres:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genres not found'
        )
    return genres
