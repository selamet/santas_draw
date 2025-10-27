#!/bin/bash
set -e

echo "🚀 Starting Santa's Draw API..."

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "⏳ Waiting for PostgreSQL..."
  sleep 1
done

echo "✅ PostgreSQL is ready!"
alembic upgrade head
echo "🎄 Starting application..."

exec "$@"
