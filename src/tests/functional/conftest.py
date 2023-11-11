# файл со всеми общими фикстурами для тестов.

import aiohttp
import asyncio
import pytest_asyncio
import pytest
from elasticsearch import AsyncElasticsearch, Elasticsearch
from elasticsearch.helpers import async_bulk

from redis.asyncio import Redis

from .settings import test_settings
from .utils.helpers import get_es_bulk_query


# Этот аргумент позволяет выполнить фикстуру перед всеми тестами и завершить после всех тестов
@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(
        hosts=[f'{test_settings.es_host}:{test_settings.es_port}', ])
    yield client
    await client.close()


@pytest_asyncio.fixture(scope='session')
async def fastapi_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


def pytest_sessionstart(session):
    """Удаляет все существующие индесы из эластика и создаем необходимые индесы в эластике перед началом тестирования."""
    es_client = Elasticsearch(
        hosts=[f'{test_settings.es_host}:{test_settings.es_port}', ])

    es_indicies = [test_settings.es_movies_index,
                   test_settings.es_persons_index, test_settings.es_genres_index]
    es_client.indices.delete(
        index=es_indicies, ignore=404)

    es_client.indices.create(index=test_settings.es_movies_index,
                             body=test_settings.es_index_movies_mapping, ignore=400)
    es_client.indices.create(index=test_settings.es_persons_index,
                             body=test_settings.es_index_persons_mapping, ignore=400)
    es_client.indices.create(index=test_settings.es_genres_index,
                             body=test_settings.es_index_genres_mapping, ignore=400)


@pytest_asyncio.fixture(autouse=True)
def es_clean_all_data(es_client: AsyncElasticsearch):
    """Удаляет все данные из индексов эластика перед каждым тестом."""
    query_clean_all = {
        "query": {
            "match_all": {}
        }
    }
    es_client.delete_by_query(index='_all', body=query_clean_all)


@pytest_asyncio.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], index: str):
        bulk_query = get_es_bulk_query(data, index, test_settings.es_id_field)
        success, errors = await async_bulk(es_client, bulk_query)
        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

        return success, errors
    return inner


@pytest_asyncio.fixture
def make_get_request(fastapi_session: aiohttp.ClientSession):
    async def inner(endpoint: str, query_data: dict = None):
        url = test_settings.service_url + f'/api/v1/{endpoint}'
        response = await fastapi_session.get(url, params=query_data)
        body = await response.json() if response.headers['Content-type'] == 'application/json' else response.text()
        headers = response.headers
        status = response.status

        response = {
            'body': body,
            'headers': headers,
            'status': status
        }
        return response
    return inner


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    client = Redis(
        host=test_settings.redis_host, port=test_settings.redis_port)
    yield client
    await client.close()


@pytest_asyncio.fixture
def redis_get(redis_client: Redis):
    async def inner(key: str):
        value = await redis_client.get(key)
        return value
    return inner


@pytest_asyncio.fixture
def redis_set(redis_client: Redis):
    async def inner(key: str, value: str):
        await redis_client.set(key, value)
        return
    return inner
