from uuid import UUID
from http import HTTPStatus
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from services.film import FilmService, get_film_service
from models.film import Film, FilmShort


router = APIRouter()


@router.get(
    '/search',
    response_model=List[FilmShort],
    summary='Поиск кинопроизведений',
    description='Выполняет полнотекстовый поиск кинопроизведений',
    response_description='Список кинопроизведений с названием и рейтингом',
)
async def search_film(
    query: str,
    page_size: Annotated[int, Query(ge=1)] = 50,
    page_number: Annotated[int, Query(ge=1)] = 1,
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
    response_model=Film,
    summary='Полная информация по кинопроизведению',
    description='Получение полной информации о кинопроизведении по его идентификатору',
    response_description='Полная информация о кинопроизведении',
)
async def film_details(
    film_id: UUID,
    film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_film_by_id(film_id)

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='film not found'
        )
    return film


@router.get(
    '/',
    response_model=List[FilmShort],
    summary='Список отсортированных кинопроизведений',
    description='Выполняет поиск кинопроизведений с опциональной фильтрацией по жанру и сортировкой',
    response_description='Список кинопроизведений с названием и рейтингом',
)
async def films(
    genre_id: UUID = Query(None),
    sort: str = Query('-imdb_rating'),
    page_size: Annotated[int, Query(ge=1)] = 50,
    page_number: Annotated[int, Query(ge=1)] = 1,
    film_service: FilmService = Depends(get_film_service)
) -> List[FilmShort]:
    if genre_id:
        films = await film_service.get_films_by_genre_id_with_sort(
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
