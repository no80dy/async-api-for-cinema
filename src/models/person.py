from typing import Optional, List

from models.film import BaseModelOrjson


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
