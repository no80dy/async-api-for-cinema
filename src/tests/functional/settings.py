# настройки для тестов
from pydantic_settings import BaseSettings

from .testdata.es_mapping import es_shema_movies


class TestSettings(BaseSettings):
    project_name: str = 'movies'

    redis_host: str = 'redis'
    redis_port: int = 6379

    es_host: str = 'elastic'
    es_port: int = 9200
    es_id_field: str = 'id'  # TODO: заполнил исходя из названия айди в дампе предыдущего проекта, не уверен что верно
    es_index_mapping: dict = es_shema_movies  # TODO: здесь только по фильмам, вероятно нужно добавить еще по жанрам и персонам
    es_index: str = 'movies'  # TODO: пока что только для фильмов. для персон и жанров отдельно делать?

    service_url: str = 'http://127.0.0.1:8000'


test_settings = TestSettings()
