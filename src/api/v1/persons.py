from uuid import UUID
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from services.person import PersonService, get_person_service


router = APIRouter()


class UUIDMixin(BaseModel):
    id: UUID = Field(serialization_alias='uuid')


class PersonRoles(UUIDMixin):
    """Список ролей, которые персона исполнила в конкретном кинопроизведении"""
    roles: list[str]


class Person(UUIDMixin):
    """
    Модель ответов для:
    /api/v1/persons/search/ - с фильтром и без
    /api/v1/persons/<uuid:UUID>/
    /api/v1/persons/<uuid:UUID>/film/
    """
    id: UUID = Field(serialization_alias='uuid')
    full_name: str
    films: list[PersonRoles]


@router.get('/search',
            response_model=list[Person],
            summary='Поиск персон',
            description='Выполняет полнотекстовый поиск персон',
            response_description='Список персон со списком фильмов и ролей, исполненных в них')
async def search_persons(query: str,
                         page_size: Annotated[int | None, Query(ge=1)] = 1,
                         page_number: Annotated[int | None, Query(ge=1)] = 1,
                         person_service: PersonService = Depends(
                             get_person_service)
                         ) -> list[Person]:

    persons = await person_service.get_persons_by_query(
        query, page_size, page_number
    )
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='persons not found')

    return [
        Person.model_validate_json(person.model_dump_json())
        for person in persons
    ]


@router.get('/{person_id}',
            response_model=Person,
            summary='Информация о персоне',
            description='Получение подробной информации о конкретной персоне',
            response_description='Информация о персоне')
async def person_details(person_id: UUID,
                         person_service: PersonService = Depends(
                             get_person_service)
                         ) -> Person:

    person = await person_service.get_person_by_id(person_id)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')

    return Person.model_validate_json(person.model_dump_json())
