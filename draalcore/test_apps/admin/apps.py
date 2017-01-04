from django.apps import AppConfig


class AdminConfig(AppConfig):
    name = 'draalcore.test_apps.admin'
    label = 'draalcore.test_apps.admin'

    public_app = True
    display_name = 'admin'
