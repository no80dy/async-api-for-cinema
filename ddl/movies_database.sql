-- create schema
CREATE SCHEMA IF NOT EXISTS content;


-- create tables
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid,
    film_work_id uuid,
    created timestamp with time zone,
    CONSTRAINT fk_genre_id
    FOREIGN KEY (genre_id)
    REFERENCES content.genre (id)
    ON DELETE CASCADE,
    CONSTRAINT fk_film_work_id
    FOREIGN KEY (film_work_id)
    REFERENCES content.film_work (id)
    ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    person_id uuid REFERENCES content.person ON DELETE CASCADE,
    film_work_id uuid REFERENCES content.film_work ON DELETE CASCADE,
    role TEXT NOT NULL,
    created timestamp with time zone,
    CONSTRAINT fk_person_id
    FOREIGN KEY (person_id)
    REFERENCES content.person (id)
    ON DELETE CASCADE,
    CONSTRAINT fk_film_work_id
    FOREIGN KEY (film_work_id)
    REFERENCES content.film_work (id)
    ON DELETE CASCADE
);


-- create indexes
-- индексы с частыми запросами на фильтрацию
CREATE INDEX ON content.film_work (creation_date, rating);
CREATE INDEX film_work_rating_idx ON content.film_work(rating);

-- индексы, которые блокирующие неправильную логику
CREATE UNIQUE INDEX film_work_person_idx ON content.person_film_work (film_work_id, person_id, role);
CREATE UNIQUE INDEX film_work_genre_idx ON content.genre_film_work (genre_id, film_work_id);
