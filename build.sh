#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

PYTHON_CMD=python
command -v python >/dev/null 2>&1 || PYTHON_CMD=python3

echo "==> Python: $($PYTHON_CMD --version)"
if [ -n "$DATABASE_URL" ]; then
  echo "==> DATABASE_URL set: yes"
else
  echo "==> DATABASE_URL set: no"
fi

# تحقق سريع من سائق PostgreSQL قبل migrate
$PYTHON_CMD - <<'PY'
import os, sys
url = os.environ.get("DATABASE_URL", "")
if url.startswith("postgres"):
    try:
        import psycopg  # noqa: F401
        print("==> psycopg OK")
    except Exception as e:
        print("==> FATAL: PostgreSQL driver missing:", e)
        sys.exit(1)
else:
    print("==> Using SQLite (no DATABASE_URL)")
PY

$PYTHON_CMD manage.py migrate --no-input
$PYTHON_CMD manage.py collectstatic --no-input
$PYTHON_CMD manage.py setup_groups
$PYTHON_CMD manage.py seed_data
echo "==> Build finished OK"
