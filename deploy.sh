#!/bin/bash

# Railway Deployment Script
echo "🚀 Starting Railway deployment..."

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Make sure you're in the project root."
    exit 1
fi

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Check if we're in production
if [ "$RAILWAY_ENVIRONMENT" = "production" ]; then
    echo "🌐 Starting production server..."
    gunicorn django_walking_buddy.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
else
    echo "🔧 Starting development server..."
    cd walking-buddy-app
    .\venv\Scripts\Activate.ps1
    python manage.py runserver
fi 