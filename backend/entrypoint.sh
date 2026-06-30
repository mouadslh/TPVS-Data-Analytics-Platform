#!/bin/bash
set -e

echo "Waiting for MySQL..."
until python -c "
import socket, os
s = socket.socket()
s.settimeout(2)
try:
    s.connect((os.environ.get('MYSQL_HOST', 'mysql'), int(os.environ.get('MYSQL_PORT', 3306))))
    s.close()
    exit(0)
except Exception:
    exit(1)
" 2>/dev/null; do
  sleep 2
done

echo "Waiting for PostgreSQL..."
until python -c "
import socket, os
s = socket.socket()
s.settimeout(2)
try:
    s.connect((os.environ.get('POSTGRES_HOST', 'postgres'), int(os.environ.get('POSTGRES_PORT', 5432))))
    s.close()
    exit(0)
except Exception:
    exit(1)
" 2>/dev/null; do
  sleep 2
done

echo "Waiting for Redis..."
until python -c "
import socket, os
s = socket.socket()
s.settimeout(2)
try:
    s.connect((os.environ.get('REDIS_HOST', 'redis'), int(os.environ.get('REDIS_PORT', 6379))))
    s.close()
    exit(0)
except Exception:
    exit(1)
" 2>/dev/null; do
  sleep 2
done

python manage.py migrate --noinput

# Initialize DWH schema and seed data on first boot
python manage.py init_dwh 2>/dev/null || true
python manage.py seed_data --agents 50 --days 180 2>/dev/null || true

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
