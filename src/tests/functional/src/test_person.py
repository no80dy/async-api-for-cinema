# from ....services.person import ElasticPersonHandler
import copy
import json
import pytest
import uuid

import asyncio

from ..settings import test_settings
from ..testdata.es_data import es_data, es_persons_data, es_person_films_data, person_cach_data


HTTP_200 = 200
HTTP_404 = 404
HTTP_422 = 422


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id': es_persons_data[0].get('id')},
            {'status': HTTP_200,
             'body': copy.deepcopy(es_persons_data[0])
             }
        ),
    ]
)
@pytest.mark.asyncio
async def test_person(es_write_data, make_get_request, query_data, expected_answer):
    # Загружаем данные в ES
    await es_write_data(es_persons_data, test_settings.es_persons_index)

    # Запрашиваем данные из ES
    response = await make_get_request(f"persons/{query_data.get('id')}")

    # Проверяем ответ
    assert (
        response.get('status') == expected_answer.get('status')
    ), 'При позитивном сценарии поиска персоны, ответ отличается от 200'

    expected_answer.get('body')['uuid'] = expected_answer.get('body').pop('id')
    for film in expected_answer.get('body')['films']:
        film['uuid'] = film.pop('id')
    assert (
        response.get('body') == expected_answer.get('body')
    ), 'При позитивном сценарии поиска персоны, тело ответа отличается от ожидаемого'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # ID, которого нет в БД
        (
            {'id': str(uuid.uuid4())},
            {'status': HTTP_404}
        ),
        # Не валидный ID
        (
            {'id': '1'},
            {'status': HTTP_422}
        ),
    ]
)
@pytest.mark.asyncio
async def test_person_negative(make_get_request, query_data, expected_answer):
    response = await make_get_request(f"persons/{query_data.get('id')}")

    assert response.get(
        'status') == expected_answer.get('status'), 'при несуществующих значениях, получен ответ отличный от 404'
    assert response.get(
        'status') == expected_answer.get('status'), 'при невалидных значениях, получен ответ отличный от 422'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id': es_person_films_data[0].get('id')},
            {'status': HTTP_200,
             'body': [{
                 'uuid':  es_data[0].get('id'),
                 'title': es_data[0].get('title'),
                 'imdb_rating': es_data[0].get('imdb_rating')
             },]
             }
        ),
    ]
)
@pytest.mark.asyncio
async def test_person_films(es_write_data, make_get_request, query_data, expected_answer):
    # Загружаем данные в ES
    await es_write_data(es_data, test_settings.es_movies_index)
    await es_write_data(es_person_films_data, test_settings.es_persons_index)

    # Запрашиваем данные из ES
    # Без этого костыля, данный тест иногда выполняется, обычно нет - видимо какая-то гонка, но как понять где?
    await asyncio.sleep(1)

    response = await make_get_request(f"persons/{query_data.get('id')}/film")

    # Проверяем ответ
    assert (
        response.get('status') == expected_answer.get('status')
    ), 'При позитивном сценарии поиска фильмов персоны, ответ отличается от 200'

    assert (
        response.get('body') == list(expected_answer.get('body'))
    ), 'При позитивном сценарии поиска фильмов персоны, тело ответа отличается от ожидаемого'


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        # ID, которого нет в БД
        (
            {'id': str(uuid.uuid4())},
            {'status': HTTP_404}
        ),
        # Не валидный ID
        (
            {'id': '1'},
            {'status': HTTP_422}
        ),
    ]
)
@pytest.mark.asyncio
async def test_person_films_negative(make_get_request, query_data, expected_answer):
    response = await make_get_request(f"persons/{query_data.get('id')}/film")

    assert response.get(
        'status') == expected_answer.get('status'), 'при несуществующих значениях, получен ответ отличный от 404'
    assert response.get(
        'status') == expected_answer.get('status'), 'при невалидных значениях, получен ответ отличный от 422'


# поиск с учётом кеша в Redis


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id': person_cach_data[0].get('id')},
            {'body': person_cach_data[0]}
        ),
    ]
)
@pytest.mark.asyncio
async def test_person_cach(redis_get, es_write_data, make_get_request, query_data, expected_answer):
    """После запроса персоны по апи, идем в редис и ожидаем увидеть там запрошенную персону."""
    await es_write_data(person_cach_data, test_settings.es_persons_index)
    await make_get_request(f"persons/{query_data.get('id')}")

    key = str(query_data.get('id'))
    value = await redis_get(key)

    assert json.loads(value) == expected_answer.get('body')


@pytest.mark.asyncio
async def test_person_cach(redis_set, make_get_request):
    """Кладем в редис персону, которой точно нет в эластике. При запросе - ожидаем ответ из кеша."""
    key = str(str(uuid.uuid4()))
    value = {
        'id': key,
        'full_name': 'Absent in ES',
        'films': [
            {'id': str(uuid.uuid4()), 'roles': ['Writer']},
        ]
    }
    expected_value = {
        'uuid': key,
        'full_name': 'Absent in ES',
        'films': [
            {'uuid': value.get('films')[0].get('id'), 'roles': ['Writer']},
        ]
    }
    await redis_set(key, json.dumps(value))
    response = await make_get_request(f"persons/{key}")

    assert response.get('status') == HTTP_200
    assert response.get('body') == expected_value


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id': es_person_films_data[0].get('id')},
            {'body': {
                'id': es_data[0].get('id'),
                'title': es_data[0].get('title'),
                'description': es_data[0].get('description'),
                'imdb_rating': es_data[0].get('imdb_rating'),
                'genres': es_data[0].get('genres'),
                'directors': es_data[0].get('directors'),
                'actors': es_data[0].get('actors'),
                'writers': es_data[0].get('writers'),
            }, }
        ),
    ]
)
@pytest.mark.asyncio
async def test_person_films_cach(redis_get, es_write_data, make_get_request, query_data, expected_answer):
    """После запроса фильмов персоны по апи, идем в редис и ожидаем увидеть там список фильмов персоны."""
    await es_write_data(es_data, test_settings.es_movies_index)
    await es_write_data(es_person_films_data, test_settings.es_persons_index)

    # asyncio.sleep(1)

    await make_get_request(f"persons/{query_data.get('id')}/film")

    key = str(expected_answer.get('body').get('id'))
    value = await redis_get(key)

    assert json.loads(value) == expected_answer.get('body')


# @pytest.mark.parametrize(
#     'query_data, expected_answer',
#     [
#         (
#             {'id': es_person_films_data[0].get('id')},
#             {'body': [{'id': es_data[0].get('id'),
#                       'title': es_data[0].get('id'),
#                        'imdb_rating': es_data[0].get('id')
#                        },
#                       ]
#              }
#         ),
#     ]
# )
# @pytest.mark.asyncio
# async def test_person_cach(redis_set, es_write_data, make_get_request, query_data, expected_answer):
#     """Кладем в редис список фильмов персоны, которой точно нет в эластике. При запросе - ожидаем ответ из кеша."""
#     await es_write_data(es_person_films_data, test_settings.es_persons_index)

#     films_id = [film.get('id') for film in expected_answer.get('body')]
#     key = '/'.join(films_id)
#     value = str(expected_answer.get('body'))

#     await redis_set(key, value)
#     response = await make_get_request(f"persons/{query_data.get('id')}/film")

#     assert response.get('status') == HTTP_200
#     assert response.get('body') == expected_answer.get('body')
