import pytest
import uuid

from ..settings import test_settings
from ..testdata.es_data import es_persons_data, es_person_films_data


HTTP_200 = 200
HTTP_404 = 404
HTTP_422 = 422


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'id': es_persons_data[0].get('id')},
            {'status': HTTP_200,
             'body': es_persons_data[0]
             }
        ),
    ]
)
@pytest.mark.asyncio
async def test_person1(es_write_data, make_get_request, query_data, expected_answer):
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
        (
            {'id': es_persons_data[0].get('id')},
            {'status': HTTP_200,
             'body': es_persons_data[0]
             }
        ),
    ]
)
@pytest.mark.asyncio
async def test_person2(es_write_data, make_get_request, query_data, expected_answer):
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


# @pytest.mark.parametrize(
#     'query_data, expected_answer',
#     [
#         (
#             {'id': es_person_films_data[0].get('id')},
#             {'status': HTTP_200,
#              'body': es_person_films_data[0].get('films')
#              }
#         ),
#     ]
# )
# @pytest.mark.asyncio
# async def test_person_films(es_write_data, make_get_request, query_data, expected_answer):
#     # Загружаем данные в ES
#     await es_write_data(es_person_films_data, test_settings.es_persons_index)

#     # Запрашиваем данные из ES
#     response = await make_get_request(f"persons/{query_data.get('id')}/film")

#     # Проверяем ответ
#     assert (
#         response.get('status') == expected_answer.get('status')
#     ), 'При позитивном сценарии поиска фильмов персоны, ответ отличается от 200'

#     for film in expected_answer.get('body'):
#         film['uuid'] = film.pop('id')
#     assert (
#         response.get('body') == expected_answer.get('body')
#     ), 'При позитивном сценарии поиска фильмов персоны, тело ответа отличается от ожидаемого'
