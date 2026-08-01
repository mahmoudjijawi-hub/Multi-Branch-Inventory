#!/usr/bin/env bash
set -o errexit

PYTHON_CMD=python
command -v python >/dev/null 2>&1 || PYTHON_CMD=python3

# إجبار SQLite دائماً
unset DATABASE_URL
export USE_SQLITE=True

echo "==> Preparing SQLite database..."
$PYTHON_CMD manage.py migrate --no-input
$PYTHON_CMD manage.py setup_groups
$PYTHON_CMD manage.py seed_data

echo "==> Starting gunicorn..."
exec $PYTHON_CMD -m gunicorn inventory_system.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 1 --timeout 120
