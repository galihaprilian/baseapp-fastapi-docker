#! /usr/bin/env bash

# Let the DB start
echo "Waiting for database..."

while ! nc -z $POSTGRES_SERVER 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Run migrations
#alembic upgrade head

# Create initial data in DB
python /app/app/initial_data.py

