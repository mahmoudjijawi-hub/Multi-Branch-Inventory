#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

PYTHON_CMD=python
command -v python >/dev/null 2>&1 || PYTHON_CMD=python3

$PYTHON_CMD manage.py migrate --no-input
$PYTHON_CMD manage.py collectstatic --no-input
$PYTHON_CMD manage.py setup_groups
$PYTHON_CMD manage.py seed_data
