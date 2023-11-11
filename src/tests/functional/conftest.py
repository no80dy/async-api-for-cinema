# файл со всеми общими фикстурами для тестов.

import aiohttp
import pytest
import pytest_asyncio
import asyncio
from typing import Any
from elasticsearch import AsyncElasticsearch, Elasticsearch
from redis.asyncio import Redis

from .settings import test_settings
from .utils.helpers import get_es_bulk_query


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    async with AsyncElasticsearch(hosts=[f'{test_settings.es_host}:{test_settings.es_port}', ]) as client:
        yield client


@pytest_asyncio.fixture(scope='session')
async def redis_client() -> Redis:
    async with Redis(host=test_settings.redis_host, port=test_settings.redis_port) as client:
        yield client


@pytest_asyncio.fixture(scope='session')
async def fastapi_session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest_asyncio.fixture(scope='session', autouse=True)
async def es_create_schema(es_client: AsyncElasticsearch):
    await es_client.indices.create(index=test_settings.es_movies_index, body=test_settings.es_index_movies_mapping)
    await es_client.indices.create(index=test_settings.es_persons_index, body=test_settings.es_index_persons_mapping)
    await es_client.indices.create(index=test_settings.es_genres_index, body=test_settings.es_index_genres_mapping)

    yield

    await es_client.indices.delete(index=test_settings.es_movies_index)
    await es_client.indices.delete(index=test_settings.es_genres_index)
    await es_client.indices.delete(index=test_settings.es_persons_index)


@pytest_asyncio.fixture(scope='function')
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], index):
        bulk_query = get_es_bulk_query(data, index, test_settings.es_id_field)
        str_query = '\n'.join(bulk_query) + '\n'
        response = await es_client.bulk(str_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest_asyncio.fixture(scope='function')
def make_get_request(fastapi_session: aiohttp.ClientSession):
    async def inner(endpoint: str, query_data: dict):
        url = test_settings.service_url + f'/api/v1/{endpoint}'
        async with fastapi_session.get(url, params=query_data) as response:
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
