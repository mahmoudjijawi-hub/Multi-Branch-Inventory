#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python3 manage.py migrate --no-input
python3 manage.py setup_groups
python3 manage.py seed_data
python3 manage.py collectstatic --no-input
