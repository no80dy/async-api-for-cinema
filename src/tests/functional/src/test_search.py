import datetime
import uuid
import json

import aiohttp
import pytest

from elasticsearch import AsyncElasticsearch


#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
                {'query': 'Star'},
                {'status': 200, 'length': 50}
        ),
        (
                {'query': 'Mashed'},
                {'status': 200, 'length': 0}
        ),
    ]
)
@pytest.mark.asyncio
async def test_search(make_get_request, es_write_data, query_data, expected_answer):
    # 1. Генерируем данные для ES

    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genres': [{'id': str(uuid.uuid4()), 'name': 'Action'}],
        'title': 'The Star',
        'description': 'New World',
        'director': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': str(uuid.uuid4()), 'name': 'Ann'},
            {'id': str(uuid.uuid4()), 'name': 'Bob'}
        ],
        'writers': [
            {'id': str(uuid.uuid4()), 'name': 'Ben'},
            {'id': str(uuid.uuid4()), 'name': 'Howard'}
        ],
        'created_at': datetime.datetime.now().isoformat(),
        'updated_at': datetime.datetime.now().isoformat(),
        'film_work_type': 'movie'
    } for _ in range(60)]

    # Загружаем данные в ES
    await es_write_data(es_data)

    # 3. Запрашиваем данные из ES по API
    response = await make_get_request('/search', query_data)  # TODO разобраться он хочет подставить в фикстуре make_get_request вместо параметров внутренней inner

    # 4. Проверяем ответ
    assert response.get('status') == expected_answer.get('status')
    assert len(response.get('body')) == expected_answer.get('length')
