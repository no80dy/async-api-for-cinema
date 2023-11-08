import pytest

from ..settings import test_settings
from ..testdata.es_data import es_data


HTTP_200 = 200
HTTP_422 = 422


#  Название теста должно начинаться со слова `test_`
#  Любой тест с асинхронными вызовами нужно оборачивать декоратором `pytest.mark.asyncio`, который следит за запуском и работой цикла событий.

@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # дефолтная пагинация
        (
                {'query': 'Star'},
                {'status': HTTP_200, 'length': 50}
        ),
        (
                {'query': 'Mashed'},
                {'status': HTTP_200, 'length': 0}
        ),
        (
                {'query': ''},
                {'status': HTTP_200, 'length': 0}
        ),

        # передаем значения пагинации
        (
                {'query': 'Star', 'page_size': 10, 'page_number': 1},
                {'status': HTTP_200, 'length': 10}
        ),
        (
                {'query': 'Star', 'page_size': 100, 'page_number': 1},
                {'status': HTTP_200, 'length': 50}
        ),
        (
                {'query': 'Mashed', 'page_size': 10, 'page_number': 1},
                {'status': HTTP_200, 'length': 0}
        ),
        (
                {'query': '', 'page_size': 10, 'page_number': 1},
                {'status': HTTP_200, 'length': 0}
        ),

        # передается часть параметров пагинации
        (
                {'query': 'Star', 'page_size': 10},
                {'status': HTTP_200, 'length': 10}
        ),
        (
                {'query': 'Star', 'page_number': 1},
                {'status': HTTP_200, 'length': 50}
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_films_positive(make_get_request, es_write_data, query_data, expected_answer):
    # Загружаем данные в ES
    await es_write_data(es_data, test_settings.es_movies_index)

    # 3. Запрашиваем данные из ES по API
    response = await make_get_request('/search', query_data)

    # 4. Проверяем ответ
    assert (
            response.get('status') == expected_answer.get('status')
    ), 'При позитивном сценарии поиска фильмов, ответ отличается от 200'

    assert (
            len(response.get('body')) == expected_answer.get('length')
    ), 'При позитивном сценарии поиска фильмов, длина тела ответа отличается от ожидаемого'


@pytest.mark.parametrize(
    'query_data, expected_http_code',
    [
        # невалидные значения пагинации
        (
                {'query': 'Star', 'page_size': -10, 'page_number': -1},
                HTTP_422,
        ),
        (
                {'query': 'Mashed', 'page_size': 10, 'page_number': -1},
                HTTP_422,
        ),
        (
                {'query': '', 'page_size': -10, 'page_number': 1},
                HTTP_422,
        ),

        # передается часть параметров пагинации невалидными
        (
                {'query': 'Star', 'page_size': -10},
                HTTP_422,
        ),
        (
                {'query': 'Star', 'page_number': -1},
                HTTP_422,
        ),

        (
                {'query': 'Star', 'page_size': -5},
                HTTP_422,
        ),
    ]
)
@pytest.mark.asyncio
async def test_search_films_negative(make_get_request, es_write_data, query_data, expected_http_code):
    # Загружаем данные в ES
    await es_write_data(es_data, test_settings.es_movies_index)

    # 3. Запрашиваем данные из ES по API
    response = await make_get_request('/search', query_data)

    # 4. Проверяем ответ
    assert response.get('status') == expected_http_code, 'при невалидных значениях, получен ответ отличный от 422'
