from typing import Optional, List

from models.film import BaseModelOrjson


class PersonRoles(BaseModelOrjson):
    roles: Optional[List[str]]


class Person(BaseModelOrjson):
    """Внутренняя модель, используется только в рамках бизнес-логики."""
    full_name: str
    films: Optional[List[PersonRoles]]
