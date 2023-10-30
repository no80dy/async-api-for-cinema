# файл со всеми общими фикстурами для тестов.
import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

# from tests.functional.settings import test_settings


from .settings import test_settings


@pytest.fixture(scope='session')  # Этот аргумент позволяет выполнить фикстуру перед всеми тестами и завершить после всех тестов
async def es_client():
    client = AsyncElasticsearch(hosts=[f'{test_settings.es_host}:{test_settings.es_port}', ],
                                   validate_cert=False,
                                   use_ssl=False)
    yield client
    await client.close()


@pytest.fixture(scope='session')  # Этот аргумент позволяет выполнить фикстуру перед всеми тестами и завершить после всех тестов
async def fastapi_session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(data: list[dict]):
        bulk_query = get_es_bulk_query(data, test_settings.es_index, test_settings.es_id_field)
        str_query = '\n'.join(bulk_query) + '\n'

        response = await es_client.bulk(str_query, refresh=True)
        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest.fixture
def make_get_request(fastapi_session: aiohttp.ClientSession):  # TODO: разобраться когда здесь фикстуру принимаем, как параметры правильно принимать для внутренней функции
    async def inner(endpoint: str, query_data: dict):
        url = test_settings.service_url + f'/api/v1{endpoint}'
        async with fastapi_session.get(url, params=query_data) as response:
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




# # нагуглил как параметры прокинуть в фикстуру
# @pytest.fixture(params=['dir1_fixture', 'dir2_fixture'])
# def dirname(request):
#     return request.getfixturevalue(request.param)
