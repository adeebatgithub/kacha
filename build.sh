#!/usr/bin/env bash
set -o errexit
set -o pipefail

echo "Installing dependencies..."
pip install -r req.txt

echo "Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser (if it does not already exist)..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()

username = "root"
password = "root"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password)
    print("Superuser created.")
else:
    print("Superuser already exists. Skipping.")
EOF
