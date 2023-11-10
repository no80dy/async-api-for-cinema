import uuid


DATA_ROWS = 50

es_films_data = [{
        'id': str(uuid.uuid4()),
        'title': 'The Star',
        'description': 'New World',
        'imdb_rating': 8.5,
        'genres': [
            {'id': str(uuid.uuid4()), 'name': 'Action'},
            {'id': str(uuid.uuid4()), 'name': 'Drama'}
        ],
        'directors': [
            {'id': str(uuid.uuid4()), 'name': 'Ann'},
            {'id': str(uuid.uuid4()), 'name': 'Bob'}
        ],
        'actors': [
            {'id': str(uuid.uuid4()), 'name': 'Ann'},
            {'id': str(uuid.uuid4()), 'name': 'Bob'}
        ],
        'writers': [
            {'id': str(uuid.uuid4()), 'name': 'Ben'},
            {'id': str(uuid.uuid4()), 'name': 'Howard'}
        ],
    }
    for _ in range(DATA_ROWS)]


es_persons_data = [{
    'id': str(uuid.uuid4()),
    'full_name': 'Mat Lucas',
    'films': [
        {'id': str(uuid.uuid4()), 'roles': ['Actor']},
        {'id': str(uuid.uuid4()), 'roles': ['Director', 'Writer']}
    ]
} for _ in range(DATA_ROWS)]


es_genres_data = [
    {
        'id': str(uuid.uuid4()),
        'name': 'Action',
        'description': 'This is description'
    } for _ in range(DATA_ROWS)]
