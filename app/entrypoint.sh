#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$1" == "run" ]; then
    python manage.py migrate
    python manage.py collectstatic --no-input --clear
    python manage.py test
    python manage.py runserver 127.0.0.1:8000
fi

exec "$@"