from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from db.redis import RedisCache
from db.elastic import ElasticStorage
from api.v1 import films, genres, persons
from core.config import settings

from db import cache
from db import elastic


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключаемся к базам данных при включении сервера
    cache.cache = RedisCache(host=settings.redis_host, port=settings.redis_port)
    elastic.es = ElasticStorage([f'{settings.es_host}:{settings.es_port}', ])
    yield
    # Отключаемся от баз при выключении сервера
    await cache.cache.close()
    await elastic.es.close_instance()


app = FastAPI(
    description='Информация о фильмах, жанрах и людях, участвовавших в создании произведения',
    version='1.0.0',
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=settings.project_name,
    # Адрес документации в красивом интерфейсе
    docs_url='/api/openapi',
    # Адрес документации в формате OpenAPI
    openapi_url='/api/openapi.json',
    default_response_class=JSONResponse,
    lifespan=lifespan
)


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])


if __name__ == '__main__':
    # Приложение может запускаться командой
    # `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )
