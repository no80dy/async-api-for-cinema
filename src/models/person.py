from typing import Optional, List

from models.film import BaseProjectModel


class PersonRoles(BaseProjectModel):
    roles: Optional[List[str]]


class Person(BaseProjectModel):
    """Внутренняя модель, используется только в рамках бизнес-логики."""
    full_name: str
    films: Optional[List[PersonRoles]]
