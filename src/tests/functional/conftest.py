# файл со всеми общими фикстурами для тестов.
import datetime
import uuid
import json

import aiohttp
import asyncio
import pytest_asyncio
import pytest

from elasticsearch import AsyncElasticsearch, Elasticsearch
from elasticsearch.helpers import async_bulk

# from tests.functional.settings import test_settings


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
    es_client = Elasticsearch(
        hosts=[f'{test_settings.es_host}:{test_settings.es_port}', ])

    es_client.indices.create(index=test_settings.es_movies_index,
                             body=test_settings.es_index_movies_mapping, ignore=400)
    es_client.indices.create(index=test_settings.es_persons_index,
                             body=test_settings.es_index_persons_mapping, ignore=400)
    es_client.indices.create(index=test_settings.es_genres_index,
                             body=test_settings.es_index_genres_mapping, ignore=400)


# def pytest_sessionfinish(session, exitstatus=0):
#     es_client = Elasticsearch(
#         hosts=[f'{test_settings.es_host}:{test_settings.es_port}', ])

#     es_client.indices.delete(index=test_settings.es_movies_index)
#     es_client.indices.delete(index=test_settings.es_genres_index)
#     es_client.indices.delete(index=test_settings.es_persons_index)


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
        body = await response.json()
        headers = response.headers
        status = response.status

        response = {
            'body': body,
            'headers': headers,
            'status': status
        }
        return response
    return inner
