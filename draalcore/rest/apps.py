from django.apps import AppConfig


class RestConfig(AppConfig):
    default = True
    name = 'draalcore.rest'
    label = 'draalcore_rest'

    def ready(self):
        # Import signal handlers
        from draalcore.rest.handlers import create_auth_token  # noqa
