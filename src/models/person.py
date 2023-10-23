from typing import Optional, List

from models.film import BaseProjectModel


class PersonRoles(BaseProjectModel):
    roles: Optional[List[str]]


class Persons(BaseProjectModel):
    """
    Схемы ответов для:
    /api/v1/persons/search/
    /api/v1/persons/<uuid:UUID>/
    """
    full_name: str
    films: Optional[List[PersonRoles]]
