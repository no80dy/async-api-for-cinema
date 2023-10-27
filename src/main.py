import uvicorn
from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core import config
from db import elastic, redis
from api.v1 import films, genres, persons


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключаемся к базам данных при включении сервера
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}', ]
    )
    yield
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()


app = FastAPI(
    description='Информация о фильмах, жанрах и людях, участвовавших в создании произведения',
    version='1.0.0',
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=config.PROJECT_NAME,
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
