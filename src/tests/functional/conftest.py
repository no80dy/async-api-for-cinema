# файл со всеми общими фикстурами для тестов.
import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch, Elasticsearch

# from tests.functional.settings import test_settings


from .settings import test_settings
from .utils.helpers import get_es_bulk_query


@pytest.fixture(scope='session', autouse=True)
def es_create_schema(es_client):
    client = Elasticsearch(hosts=[f'{test_settings.es_host}:{test_settings.es_port}', ])
    # client.indices.create(index=test_settings.es_movies_index, body=test_settings.es_index_movies_mapping)
    client.indices.create(index=test_settings.es_persons_index, body=test_settings.es_index_persons_mapping)
    client.indices.create(index=test_settings.es_genres_index, body=test_settings.es_index_genres_mapping)

    yield
    # client.indices.delete(index=test_settings.es_movies_index)
    client.indices.delete(index=test_settings.es_genres_index)
    client.indices.delete(index=test_settings.es_persons_index)



@pytest.fixture(scope='session')  # Этот аргумент позволяет выполнить фикстуру перед всеми тестами и завершить после всех тестов
async def es_client():
    client = AsyncElasticsearch(hosts=[f'{test_settings.es_host}:{test_settings.es_port}', ])
    yield client
    await client.close()


@pytest.fixture
async def fastapi_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='session')
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict], index):
        bulk_query = get_es_bulk_query(data, index, test_settings.es_id_field)
        str_query = '\n'.join(bulk_query) + '\n'
        async for client in es_client:
            response = await client.bulk(str_query, refresh=True)
            if response['errors']:
                raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest.fixture
def make_get_request(fastapi_session: aiohttp.ClientSession):  # TODO: разобраться когда здесь фикстуру принимаем, как параметры правильно принимать для внутренней функции
    async def inner(endpoint: str, query_data: dict):
        url = test_settings.service_url + f'/api/v1/films{endpoint}'
        async for session in fastapi_session:
            response = await session.get(url, params=query_data)
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
