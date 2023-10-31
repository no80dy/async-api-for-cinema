# import datetime
# import uuid
# import json
#
# import aiohttp
# import pytest
#
# from elasticsearch import AsyncElasticsearch
#
#
# #  Название теста должно начинаться со слова `test_`
# #  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.
#
# @pytest.mark.parametrize(
#     'query_data, expected_answer',
#     [
#         (
#                 {'search': 'The Star'},
#                 {'status': 200, 'length': 50}
#         ),
#         (
#                 {'search': 'Mashed potato'},
#                 {'status': 200, 'length': 0}
#         )
#     ]
# )
# @pytest.mark.asyncio
# async def test_search(make_get_request, es_write_data, query_data, expected_answer):
#     # 1. Генерируем данные для ES
#
#     es_data = [{
#         'id': str(uuid.uuid4()),
#         'imdb_rating': 8.5,
#         'genre': ['Action', 'Sci-Fi'],
#         'title': 'The Star',
#         'description': 'New World',
#         'director': ['Stan'],
#         'actors_names': ['Ann', 'Bob'],
#         'writers_names': ['Ben', 'Howard'],
#         'actors': [
#             {'id': '111', 'name': 'Ann'},
#             {'id': '222', 'name': 'Bob'}
#         ],
#         'writers': [
#             {'id': '333', 'name': 'Ben'},
#             {'id': '444', 'name': 'Howard'}
#         ],
#         'created_at': datetime.datetime.now().isoformat(),
#         'updated_at': datetime.datetime.now().isoformat(),
#         'film_work_type': 'movie'
#     } for _ in range(60)]
#
#     # Загружаем данные в ES
#     await es_write_data(es_data)
#
#     # 3. Запрашиваем данные из ES по API
#     response = await make_get_request('/search', query_data)  # TODO разобраться он хочет подставить в фикстуре make_get_request вместо параметров внутренней inner
#
#     # 4. Проверяем ответ
#
#     assert response.status == expected_answer.get('status')
#     assert len(response.body) == expected_answer.get('length')


import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch

from ..settings import test_settings


#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.

@pytest.mark.asyncio
async def test_search():
    # 1. Генерируем данные для ES

    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': ['Action', 'Sci-Fi'],
        'title': 'The Star',
        'description': 'New World',
        'director': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': '111', 'name': 'Ann'},
            {'id': '222', 'name': 'Bob'}
        ],
        'writers': [
            {'id': '333', 'name': 'Ben'},
            {'id': '444', 'name': 'Howard'}
        ],
        'created_at': datetime.datetime.now().isoformat(),
        'updated_at': datetime.datetime.now().isoformat(),
        'film_work_type': 'movie'
    } for _ in range(60)]

    bulk_query = []
    for row in es_data:
        bulk_query.extend([
            json.dumps({'index': {'_index': test_settings.es_index, '_id': row[test_settings.es_id_field]}}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'

    # 2. Загружаем данные в ES

    es_client = AsyncElasticsearch(hosts=test_settings.es_host)
    response = await es_client.bulk(str_query, refresh=True)


    await es_client.close()
    if response['errors']:
        raise Exception('Ошибка записи данных в Elasticsearch')

    # 3. Запрашиваем данные из ES по API

    session = aiohttp.ClientSession()
    url = test_settings.service_url + '/api/v1/films/search'
    query_data = {'query': 'The Star'}
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        headers = response.headers
        status = response.status
        print('******\n')
        print('******body = ', body)

        print('\n******headers = ', headers)

        print('\n******status = ', status)
        print('******\n')
    await session.close()

    # 4. Проверяем ответ

    assert status == 200
    assert len(response.body) == 50
