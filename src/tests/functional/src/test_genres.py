import uuid
import pytest

from ..settings import test_settings
from ..testdata.es_data import es_genres_data


@pytest.mark.parametrize(
    'genre_data, expected_genre_data',
    [
        (
            {'genre_id': es_genres_data[0]['id']},
            {
                'status': 200,
                'body':
                {
                    'uuid': es_genres_data[0]['id'],
                    'name': es_genres_data[0]['name'],
                }
            }
        ),
        (
            {'genre_id': es_genres_data[1]['id']},
            {
                'status': 200,
                'body': {
                    'uuid': es_genres_data[1]['id'],
                    'name': es_genres_data[1]['name'],
                }
            }
        ),
        (
            {'genre_id': str(uuid.uuid4())},
            {
                'status': 404,
                'body': {
                    'detail': 'genres not found'
                }
            }
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

    assert response.get('status') == expected_genre_data.get('status')
    assert dict(response.get('body')) == expected_genre_data.get('body')


@pytest.mark.parametrize(
    'genre_data, expected_http_code',
    [
        (
            {'genre_id': None},
            {'status': 422}
        ),
        (
            {'genre_id': 123},
            {'status': 422}
        ),
        (
            {'genre_id': 'string'},
            {'status': 422}
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

    assert response.get('status') == expected_http_code.get('status')


@pytest.mark.parametrize(
    'expected_genre_data',
    [
        (
            {'status': 200, 'length': 50}
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

    assert response.get('status') == expected_genre_data.get('status')
    assert len(response.get('body')) == expected_genre_data.get('length')
