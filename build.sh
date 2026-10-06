#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py loaddata cleaning/fixtures/cleaning_types.json
python manage.py loaddata cleaning/fixtures/initial_data.json
python manage.py loaddata cleaning/fixtures/demo_data.json