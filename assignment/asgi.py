"""ASGI config for the assignment project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "assignment.settings")

application = get_asgi_application()
