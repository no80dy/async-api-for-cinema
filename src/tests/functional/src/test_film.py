import datetime
import uuid

import aiohttp
import pytest


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'film_id': '2669f48b-db95-481e-aa67-30706d40b320'},
            {'status': 200, }
        )
    ]
)
@pytest.mark.asyncio
async def test_specific_movie(
    make_get_request,
    es_write_data,
    film_data,
    expected_answer
):
    es_data = [{
        'id': '2669f48b-db95-481e-aa67-30706d40b320',
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
    }, ]

    await es_write_data(es_data)

    response = await make_get_request(
        '/2669f48b-db95-481e-aa67-30706d40b320',
        {}
    )

    assert response.get('status') == expected_answer.get('status'), response.get('status')
    assert dict(response.get('body'))['uuid'] == es_data[0]['id']


async def test_movie_using_cache():
    pass


async def test_all_movies():
    pass


async def test_movie_validation():
    pass