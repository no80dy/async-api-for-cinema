import uuid

es_data = [
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
        'directors': [
            {'id': str(uuid.uuid4()), 'name': 'Ben'},
            {'id': str(uuid.uuid4()), 'name': 'Howard'}
        ],
        'writers': [
            {'id': str(uuid.uuid4()), 'name': 'Ben'},
            {'id': str(uuid.uuid4()), 'name': 'Howard'}
        ],
    }
    for _ in range(60)]