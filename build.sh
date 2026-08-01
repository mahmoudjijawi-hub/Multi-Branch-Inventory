#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

PYTHON_CMD=python
command -v python >/dev/null 2>&1 || PYTHON_CMD=python3

echo "==> Python: $($PYTHON_CMD --version)"
echo "==> Using SQLite only (no external database)"

# إجبار SQLite حتى لو كان DATABASE_URL موجوداً من إعداد قديم على Render
unset DATABASE_URL
export USE_SQLITE=True

$PYTHON_CMD manage.py migrate --no-input
$PYTHON_CMD manage.py collectstatic --no-input
$PYTHON_CMD manage.py setup_groups
$PYTHON_CMD manage.py seed_data
echo "==> Build finished OK"
