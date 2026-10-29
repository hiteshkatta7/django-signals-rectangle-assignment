from django.apps import AppConfig


class SignalsDemoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "signals_demo"

    def ready(self):
        # Importing the module registers the receivers.
        from . import signals  # noqa: F401
