#!/bin/sh
set -eu
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py makemigrations shop --noinput
python manage.py migrate --noinput
