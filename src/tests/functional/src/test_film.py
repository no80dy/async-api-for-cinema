import uuid
import pytest


# Отсутствует type: nested во вложенных полях
sample_es_data = [
    {
        'id': str(uuid.uuid4()),
        'title': 'The Star',
        'description': 'New World',
        'imdb_rating': 8.5,
        'genres': [
            {'id': str(uuid.uuid4()), 'name': 'Action'},
            {'id': str(uuid.uuid4()), 'name': 'Drama'}
        ],
        'actors': [
            {'id': str(uuid.uuid4()), 'name': 'Ann'},
            {'id': str(uuid.uuid4()), 'name': 'Bob'}
        ],
        'writers': [
            {'id': str(uuid.uuid4()), 'name': 'Ben'},
            {'id': str(uuid.uuid4()), 'name': 'Howard'}
        ],
        'directors': [
            {'id': str(uuid.uuid4()), 'name': 'Ben'},
            {'id': str(uuid.uuid4()), 'name': 'Howard'}
        ],
    }
    for _ in range(50)]


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {'film_id': sample_es_data[0]['id']},
            {
                'status': 200,
                'body': sample_es_data[0]
            }
        ),
        (
            {'film_id': str(uuid.uuid4())},
            {
                'status': 404,
                'body': {
                    'detail': 'films not found'
                }
            }
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
    await es_write_data(sample_es_data)

    film_id = film_data.get('film_id')
    response = await make_get_request(
        f'/{film_id}',
        {}
    )

    assert response.get('status') == expected_answer.get('status')
    assert dict(response.get('body')) == expected_answer.get('body')


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {
                'page_size': 10,
                'page_number': 1,
            },
            {
                'status': 200,
                'length': 10,
            }
        ),
        (
            {
                'page_size': 100,
                'page_number': 1,
            },
            {
                'status': 200,
                'length': 50,
            }
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
    await es_write_data(sample_es_data)

    response = await make_get_request(
        '/',
        film_data
    )

    assert response.get('status') == expected_answer.get('status')
    assert len(response.get('body')) == expected_answer.get('length')


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {
                'page_size': 10,
                'page_number': -1
            },
            {
                'status': 422
            }
        ),
        (
            {
                'page_size': -10,
                'page_number': 1,
            },
            {
                'status': 422
            }
        ),
        (
            {
                'page_size': -10,
                'page_number': -1,
            },
            {
                'status': 422
            }
        ),
        (
            {
                'page_size': 'a',
                'page_number': -1,
            },
            {
                'status': 422
            }
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
    await es_write_data(sample_es_data)

    response = await make_get_request(
        '/',
        film_data
    )

    assert response.get('status') == expected_answer.get('status')


@pytest.mark.parametrize(
    'expected_answer',
    [
        {
            'status': 200,
            'length': 50
        },
    ]
)
@pytest.mark.asyncio
async def test_all_films(
    make_get_request,
    es_write_data,
    expected_answer
):
    await es_write_data(sample_es_data)

    response = await make_get_request(
        '/',
        {}
    )

    assert response.get('status') == expected_answer.get('status')
    assert len(response.get('body')) == expected_answer.get('length')


@pytest.mark.parametrize(
    'film_data, expected_answer',
    [
        (
            {
                'genre_id': sample_es_data[0]['genres'][0]['id']
            },
            {
                'status': 200,
            }
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
    await es_write_data(sample_es_data)

    genre_id  = film_data.get('genre_id')
    response = await make_get_request(
        '/',
        {
            'genre_id': genre_id,
        }
    )

    assert response.get('status') == expected_answer.get('status')
