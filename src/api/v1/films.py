from uuid import UUID
from typing import List
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Query

from services.film import FilmService, get_film_service
from models.film import Film


router = APIRouter()


@router.get(
    '/{film_id}',
    response_model=Film,
    summary="Поиск кинопроизведений",
    description="Полнотекстовый поиск по кинопроизведениям",
    response_description="Название и рейтинг фильма",
)
async def film_details(
    film_id: UUID,
    film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(str(film_id))

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='film not found'
        )
    return Film(id=film.id, title=film.title)


@router.get(
    '/search',
    response_model=List[Film],
    summary="Поиск кинопроизведений",
    description="Полнотекстовый поиск по кинопроизведениям",
    response_description="Название и рейтинг филкинопроизведения",
)
async def search_film(
    query: str,
    page_size: int = Query(..., ge=1),
    page_number: int = Query(..., ge=1),
    film_service: FilmService = Depends(get_film_service)
) -> List[Film]:
    films = await film_service.get_films_by_query(
        query, page_size, page_number
    )

    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='film not found'
        )
    return films
