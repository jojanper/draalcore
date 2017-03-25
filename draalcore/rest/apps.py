from django.apps import AppConfig


class RestConfig(AppConfig):
    name = 'draalcore.rest'
    label = 'draalcore.rest'

    def ready(self):
        # Import signal handlers
        from draalcore.rest.handlers import create_auth_token
