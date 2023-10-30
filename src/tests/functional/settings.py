# настройки для тестов

import os

from core.logger import LOGGING
from pydantic_settings import BaseSettings
from logging import config as logging_config


with open('./es_schema_movies.json', 'r') as f:  # TODO путь актуализировать
    es_schema_movies = f.read()


class TestSettings(BaseSettings):
    project_name: str = 'movies'

    redis_host: str = '127.0.0.1'
    redis_port: int = 6379

    es_host: str = '127.0.0.1'
    es_port: int = 9200
    es_id_field: str = 'id'  # TODO: заполнил исходя из названия айди в дампе предыдущего проекта, не уверен что верно
    es_index_mapping: dict = es_schema_movies.encode('utf-8')  # TODO: здесь только по фильмам, вероятно нужно добавить еще по жанрам и персонам
    es_index: str = 'movies'  # TODO: пока что только для фильмов. для персон и жанров отдельно делать?

    service_url: str = '127.0.0.1:8000'


test_settings = TestSettings()
