import os

from pydantic import Field
from core.logger import LOGGING
from pydantic_settings import BaseSettings
from logging import config as logging_config


class Settings(BaseSettings):
    project_name: str = Field('movies')
    redis_host: str = Field('127.0.0.1')
    redis_port: int = Field(6379)
    es_host: str = Field('127.0.0.1')
    es_port: int = Field(9200)


settings = Settings()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
