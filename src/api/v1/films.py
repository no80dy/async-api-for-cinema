from uuid import UUID
from typing import List, Optional
from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, Query

from services.film import FilmService, get_film_service
from models.film import FilmShort


router = APIRouter()


@router.get(
    '/search',
    response_model=List[FilmShort],
    summary="Поиск кинопроизведений",
    description="Полнотекстовый поиск по кинопроизведениям",
    response_description="Название и рейтинг филкинопроизведения",
)
async def search_film(
    query: str,
    page_size: int = Query(..., ge=1),
    page_number: int = Query(..., ge=1),
    film_service: FilmService = Depends(get_film_service)
) -> List[FilmShort]:
    films = await film_service.get_films_by_query(
        query, page_size, page_number
    )

    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='films not found'
        )

    return [
        FilmShort(id=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]


@router.get(
    '/{film_id}',
    response_model=FilmShort,
    summary="Поиск кинопроизведений",
    description="Полнотекстовый поиск по кинопроизведениям",
    response_description="Название и рейтинг фильма",
)
async def film_details(
    film_id: str,
    film_service: FilmService = Depends(get_film_service)
) -> FilmShort:
    film = await film_service.get_film_by_id(str(film_id))

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='film not found'
        )
    return FilmShort(
        id=film.id, title=film.title, imdb_rating=film.imdb_rating
    )


@router.get(
    '/',
    response_model=List[FilmShort],
    summary="Поиск кинопроизведений",
    description="Полнотекстовый поиск по кинопроизведениям",
    response_description="Название и рейтинг фильма",
)
async def films(
    genre_id: Optional[UUID] = None,
    sort: str = Query('-imdb_rating'),
    page_size: int = Query(..., ge=1),
    page_number: int = Query(..., ge=1),
    film_service: FilmService = Depends(get_film_service)
) -> List[FilmShort]:
    if genre_id:
        films = await film_service.get_ilms_by_genre_id_with_sort(
            genre_id, sort, page_size, page_number
        )
    else:
        films = await film_service.get_films_with_sort(
            sort, page_size, page_number
        )

    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='films not found'
        )
    return [
        FilmShort(id=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
