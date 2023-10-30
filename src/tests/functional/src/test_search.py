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
                {'search': 'The Star'},
                {'status': 200, 'length': 50}
        ),
        (
                {'search': 'Mashed potato'},
                {'status': 200, 'length': 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_search(make_get_request, es_write_data, query_data, expected_answer):
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

    # Загружаем данные в ES
    await es_write_data(es_data)

    # 3. Запрашиваем данные из ES по API
    response = await make_get_request('/search', query_data)  # TODO разобраться он хочет подставить в фикстуре make_get_request вместо параметров внутренней inner

    # 4. Проверяем ответ

    assert response.status == expected_answer.get('status')
    assert len(response.body) == expected_answer.get('length')