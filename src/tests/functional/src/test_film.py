import json
import uuid
import pytest

from ..settings import test_settings
from ..testdata.es_data import es_films_data


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'film_id': es_films_data[0]['id']},
            {'status': 200, 'body': es_films_data[0]}
        ),
        (
            {'film_id': str(uuid.uuid4())},
            {'status': 404, 'body': { 'detail': 'films not found' } }
        )
    ]
)
@pytest.mark.asyncio
async def test_search_film_by_film_id(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    film_id = film_data.get('film_id')
    response = await make_get_request(f'films/{film_id}', {})

    expected_answer['uuid'] = expected_answer.pop('id')
    assert response.get('status') == expected_answer.get('status')
    assert dict(response.get('body')) == expected_answer.get('body')


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'film_id': 'wrong_uuid'},
            {'status': 422}
        )
    ]
)
@pytest.mark.asyncio
async def test_search_film_by_film_id(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    film_id = film_data.get('film_id')
    response = await make_get_request(f'films/{film_id}', {})

    assert response.get('status') == expected_answer.get('status')


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'page_size': 10, 'page_number': 1},
            {'status': 200, 'length': 10}
        ),
        (
            {'page_size': 100, 'page_number': 1},
            {'status': 200, 'length': 50}
        )
    ]
)
@pytest.mark.asyncio
async def test_films_pagination(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    response = await make_get_request('films/', film_data)

    assert response.get('status') == expected_answer.get('status')
    assert len(response.get('body')) == expected_answer.get('length')


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'page_size': -10, 'page_number': -1},
            {'status': 422}
        ),
        (
            {'page_size': 'wrong', 'page_number': 'wrong'},
            {'status': 422}
        )
    ]
)
@pytest.mark.asyncio
async def test_wrong_films_pagination(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    response = await make_get_request('films/', film_data)

    assert response.get('status') == expected_answer.get('status')


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'genre_id': es_films_data[0]['genres'][0]['id']},
            {'status': 200}
        ),
        (
            {'genre_id': str(uuid.uuid4())},
            {'status': 404}
        )
    ]
)
@pytest.mark.asyncio
async def test_search_films_by_genre_id(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    genre_id  = film_data.get('genre_id')
    response = await make_get_request('films/', {'genre_id': genre_id})

    assert response.get('status') == expected_answer.get('status')
    assert isinstance(response.get('body'), list)


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'genre_id': 'wrong'},
            {'status': 422}
        )
    ]
)
@pytest.mark.asyncio
async def test_search_films_by_genre_id(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    genre_id  = film_data.get('genre_id')
    response = await make_get_request('films/', { 'genre_id': genre_id, })

    assert response.get('status') == expected_answer.get('status')


# @pytest.mark.parametrize(
#     'film_data, expected_answer',
#     [
#         (
#             {'film_id': es_films_data[0]['id']},
#             {'body': es_films_data[0]}
#         )
#     ]
# )
# @pytest.mark.asyncio
# async def test_film_cache(
#     make_get_request,
#     es_write_data,
#     redis_client,
#     film_data,
#     expected_answer
# ):
#     await es_write_data(es_films_data, index=test_settings.es_movies_index)
#
#     film_id = film_data.get('film_id')
#     response = await make_get_request(f'/{film_id}', {})
#
#     film_from_cache = await redis_client.get(str(film_id))
#     assert json.loads(film_from_cache)['id'] == response['body']['uuid']
