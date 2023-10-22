from models.base import BaseModelOrjson


class Genres(BaseModelOrjson):
    """
    Схемы ответов для:
    /api/v1/genres/
    /api/v1/genres/<uuid:UUID>/
    """
    name: str
