#!/bin/sh

echo "Waiting for postgres..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

# wait migrations from django...
sleep 10  # как можно было иначе осуществить ожидание миграций. кроме как через такой костыль?
# миграции в данном спринте мы не проводим, по всей видимости, т.к. накатываем дамп уже готовых данных
exec "$@"