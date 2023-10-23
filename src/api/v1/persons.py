import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.person import PersonService, get_person_service


router = APIRouter()


class PersonRoles(BaseModel):
    uuid: uuid.UUID
    roles: list[str]


class Person(BaseModel):
    """
    Модель ответов для:
    /api/v1/persons/search/ - с фильтром и без
    /api/v1/persons/<uuid:UUID>/
    """
    uuid: uuid.UUID
    full_name: str
    films: list[PersonRoles]


@router.get('/{person_id}',
            response_model=Person,
            summary='Информация о персоне',
            description='Получение подробной информации о конкретной персоне',
            response_description='Информация о персоне')
async def person_details(person_id: uuid.UUID,
                         person_service: PersonService = Depends(get_person_service)) -> Person:

    person = await person_service.get_by_id(person_id)
    print('HEY!')
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='person not found')

    return person
