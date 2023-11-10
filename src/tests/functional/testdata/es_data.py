import uuid
import datetime


DATA_ROWS = 50

es_data = [{
    'id': str(uuid.uuid4()),
    'title': 'The Star',
    'description': 'New World',
    'imdb_rating': 8.5,
    'type': 'movie',
    'genres_names': ['Action'],
    'genres': [{'id': str(uuid.uuid4()), 'name': 'Action'}],
    'directors_names': ['Stan'],
    'actors_names': ['Ann', 'Bob'],
    'writers_names': ['Ben', 'Howard'],
    'directors': [
        {'id': str(uuid.uuid4()), 'name': 'Stan'}
    ],
    'actors': [
        {'id': str(uuid.uuid4()), 'name': 'Ann'},
        {'id': str(uuid.uuid4()), 'name': 'Bob'}
    ],
    'writers': [
        {'id': str(uuid.uuid4()), 'name': 'Ben'},
        {'id': str(uuid.uuid4()), 'name': 'Howard'}
    ],
    'creation_date': datetime.datetime.now().isoformat(),
} for _ in range(60)]


# Данные для тестов эндпоинтов /persons/
es_persons_data = [{
    'id': str(uuid.uuid4()),
    'full_name': 'Mat Lucas',
    'films': [
        {'id': str(uuid.uuid4()), 'roles': ['Actor']},
        {'id': str(uuid.uuid4()), 'roles': ['Director', 'Writer']}
    ]
} for _ in range(DATA_ROWS)]

es_person_films_data = [{
    'id': es_data[0].get('actors')[0].get('id'),
    'full_name': 'Ann',
    'films': [
        {'id': es_data[0].get('id'), 'roles': ['Actor']},
    ]
}]

# es_person_films_data = [{
#     'id': es_persons_data[0].get('films')[0].get('id'),
#     'title': 'War',
#     'description': 'New World',
#     'imdb_rating': 10,
#     'type': 'movie',
#     'genres_names': ['Action'],
#     'genres': [{'id': str(uuid.uuid4()), 'name': 'Action'}],
#     'directors_names': ['Stan'],
#     'actors_names': ['Ann', 'Bob'],
#     'writers_names': ['Ben', 'Howard'],
#     'directors': [],
#     'actors': [
#         {'id': es_persons_data[0].get('id'), 'name': 'Mat Lucas'},
#     ],
#     'writers': [],
#     'creation_date': datetime.datetime.now().isoformat(),
# }]
