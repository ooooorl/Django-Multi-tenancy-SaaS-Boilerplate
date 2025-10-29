#!/bin/bash
set -e

# Default to development if DJANGO_ENV is not set
DJANGO_ENV=${DJANGO_ENV:-development}

echo "🚀 Starting Django in $DJANGO_ENV mode..."

# Ensure staticfiles directory exists
mkdir -p config/staticfiles

if [ "$DJANGO_ENV" = "development" ]; then
    echo "🔧 Fixing staticfiles permissions (dev only)..."
    chmod -R 777 config/staticfiles
fi

echo "📦 Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "🗄️ Applying database migrations..."
python manage.py migrate --no-input

if [ "$DJANGO_ENV" = "production" ]; then
    echo "🔥 Launching Gunicorn with UvicornWorker..."
    exec gunicorn config.asgi:application \
        -k uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --threads 2 \
        --timeout 120
else
    echo "💻 Launching Uvicorn with reload (dev mode)..."
    exec uvicorn config.asgi:application \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
fi

# #!/bin/bash
# # Make this an executable file
# # chmod +x docker-entrypoint.sh
# set -e

# # Ensure staticfiles directory exists and is writable
# echo "Fixing staticfiles permissions..."
# mkdir -p config/staticfiles
# chmod -R 777 config/staticfiles

# echo "Collecting Staticfiles..."
# python manage.py collectstatic --no-input

# echo "Applying migrations..."
# python manage.py migrate --no-input

# # Development
# echo "Starting Gunicorn with ASGI (Uvicorn Worker)..."
# exec uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload

# # Production
# # echo "Starting Gunicorn with ASGI (Uvicorn Worker)..."
# # exec gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
