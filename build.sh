#!/usr/bin/env bash
set -o errexit

echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python backend/manage.py collectstatic --noinput

echo "Running migrations..."
python backend/manage.py migrate

