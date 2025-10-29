import os

from celery import Celery

# Set the default Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# Replace 'your_project' with your project's name.
app = Celery("config")

# Load settings from Django settings.py, using CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all apps
app.autodiscover_tasks()
