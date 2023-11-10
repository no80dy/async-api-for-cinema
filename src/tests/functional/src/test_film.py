import json
import uuid
import pytest

from ..settings import test_settings
from ..testdata.es_data import es_films_data


FILMS_RESPONSE_DATA = [
    {
    'uuid': es_film_data['id'],
    'title': es_film_data['title'],
    'imdb_rating': es_film_data['imdb_rating'],
    'description': es_film_data['description'],
    'genres': [{
        'uuid': genre['id'],
        'name': genre['name']
    } for genre in es_film_data['genres']],
    'actors': [{
        'id': actor['id'],
        'name': actor['name']
    } for actor in es_film_data['actors']],
    'writers': [{
        'id': writer['id'],
        'name': writer['name']
    } for writer in es_film_data['writers']],
    'directors': [{
        'id': director['id'],
        'name': director['name']
    } for director in es_film_data['directors']],
} for es_film_data in es_films_data]


FILMS_SHORT_RESPONSE_DATA = [
    {
        'uuid': es_film_data['id'],
        'title': es_film_data['title'],
        'imdb_rating': es_film_data['imdb_rating']
    } for es_film_data in es_films_data]

HTTP_200 = 200
HTTP_404 = 404
HTTP_422 = 422


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'film_id': es_films_data[0]['id']},
            {'status': HTTP_200, 'body': FILMS_RESPONSE_DATA[0]}
        ),
        (
            {'film_id': es_films_data[1]['id']},
            {'status': HTTP_200, 'body': FILMS_RESPONSE_DATA[1]}
        ),
        (
            {'film_id': str(uuid.uuid4())},
            {'status': HTTP_404, 'body': { 'detail': 'films not found' } }
        )
    ]
)
@pytest.mark.asyncio
async def test_search_film_by_film_id_positive(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    film_id = film_data.get('film_id')
    response = await make_get_request(f'films/{film_id}', {})

    assert response.get('status') == expected_answer.get('status')
    assert dict(response.get('body')) == expected_answer.get('body')


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'film_id': 'string'},
            {'status': 422}
        ),
        (
            {'film_id': 0},
            {'status': 422}
        )
    ]
)
@pytest.mark.asyncio
async def test_search_film_by_film_id_negative(
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
            {'status': HTTP_200, 'length': 10}
        ),
        (
            {'page_size': 100, 'page_number': 1},
            {'status': HTTP_200, 'length': 50}
        )
    ]
)
@pytest.mark.asyncio
async def test_films_pagination_positive(
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
            {'page_size': -1, 'page_number': -1},
            {'status': HTTP_422}
        ),
        (
            {'page_size': 'string', 'page_number': 'string'},
            {'status': HTTP_422}
        )
    ]
)
@pytest.mark.asyncio
async def test_films_pagination_negative(
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
            {'status': HTTP_200, 'body': FILMS_SHORT_RESPONSE_DATA[:1]}
        ),
        (
            {'genre_id': es_films_data[1]['genres'][0]['id']},
            {'status': HTTP_200, 'body': FILMS_SHORT_RESPONSE_DATA[1:2]}
        ),
    ]
)
@pytest.mark.asyncio
async def test_get_films_by_genre_id_positive(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    await es_write_data(es_films_data, index=test_settings.es_movies_index)

    genre_id  = film_data.get('genre_id')
    response = await make_get_request('films/', {'genre_id': genre_id})

    assert response.get('status') == expected_answer.get('status')
    assert response.get('body') == expected_answer.get('body')


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'genre_id': 'string'},
            {'status': HTTP_422}
        ),
        (
            {'genre_id': 0},
            {'status': HTTP_422}
        )
    ]
)
@pytest.mark.asyncio
async def test_get_films_by_genre_id_negative(
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
