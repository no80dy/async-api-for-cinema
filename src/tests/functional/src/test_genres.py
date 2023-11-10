import uuid
import pytest

from ..settings import test_settings
from ..testdata.es_data import es_genres_data


GENRE_RESPONSE_DATA = [
    {
        'uuid': genre['id'],
        'name': genre['name']
    } for genre in es_genres_data]

HTTP_200 = 200
HTTP_422 = 422
HTTP_404 = 404


@pytest.mark.parametrize(
    'genre_data, expected_genre_data',
    [
        (
            {'genre_id': es_genres_data[0]['id']},
            {'status': HTTP_200, 'body': GENRE_RESPONSE_DATA[0]}
        ),
        (
            {'genre_id': es_genres_data[1]['id']},
            {'status': HTTP_200, 'body': GENRE_RESPONSE_DATA[1]}
        ),
        (
            {'genre_id': str(uuid.uuid4())},
            {'status': HTTP_404, 'body': {'detail': 'genres not found'}}
        ),
    ]
)
@pytest.mark.asyncio
async def test_get_genre_by_id_positive(
    make_get_request,
    es_write_data,
    genre_data,
    expected_genre_data
):
    await es_write_data(es_genres_data, index=test_settings.es_genres_index)

    genre_id = genre_data.get('genre_id')
    response = await make_get_request(f'genres/{genre_id}', {})

    assert (
        response.get('status') == expected_genre_data.get('status')
    ), 'При валидных передаче данных ответ должен быть HTTP_200 или HTTP_404'
    assert (
        response.get('body') == expected_genre_data.get('body')
    ), 'Тело жанра в ответе должно быть идентично ожидаемому жанру'


@pytest.mark.parametrize(
    'genre_data, expected_http_code',
    [
        (
            {'genre_id': 'string'},
            {'status': HTTP_422}
        ),
        (
            {'genre_id': 123},
            {'status': HTTP_422}
        ),
        (
            {'genre_id': 'string'},
            {'status': HTTP_422}
        )
    ]
)
@pytest.mark.asyncio
async def test_get_genre_by_genre_id_negative(
    make_get_request,
    es_write_data,
    genre_data,
    expected_http_code
):
    await es_write_data(es_genres_data, index=test_settings.es_genres_index)

    genre_id = genre_data.get('genre_id')
    response = await make_get_request(f'genres/{genre_id}', {})

    assert (
        response.get('status') == expected_http_code.get('status')
    ), 'При передаче невалидных данных ответ должен быть равным HTTP_422'


@pytest.mark.parametrize(
    'expected_genre_data',
    [
        (
            {'status': HTTP_200, 'length': 50}
        )
    ]
)
@pytest.mark.asyncio
async def test_get_all_genres(
    make_get_request,
    es_write_data,
    expected_genre_data
):
    await es_write_data(es_genres_data, index=test_settings.es_genres_index)

    response = await make_get_request('genres/', {})

    assert (
        response.get('status') == expected_genre_data.get('status')
    ), 'При валидных передаче данных ответ должен быть HTTP_200 или HTTP_404'
    assert (
        len(response.get('body')) == expected_genre_data.get('length')
    ), 'Количество фильмов в ответе должно быть равно количеству ожидаемых'
