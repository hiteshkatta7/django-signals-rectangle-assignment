"""Minimal settings for the Django signals + Rectangle assignment."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Assignment only - never use this key in production.
SECRET_KEY = "django-insecure-assignment-only-not-for-production"

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "signals_demo.apps.SignalsDemoConfig",
    "shapes.apps.ShapesConfig",
]

MIDDLEWARE = []

ROOT_URLCONF = "assignment.urls"

TEMPLATES = []

WSGI_APPLICATION = "assignment.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_TZ = True
