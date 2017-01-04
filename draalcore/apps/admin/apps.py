from django.apps import AppConfig


class AdminConfig(AppConfig):
    name = 'draalcore.apps.admin'
    label = 'draalcore.apps.admin'

    public_app = True
    display_name = 'admin'
