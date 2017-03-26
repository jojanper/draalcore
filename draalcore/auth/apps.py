from draalcore.app_config import BaseAppConfig


class AuthConfig(BaseAppConfig):
    name = 'draalcore.auth'
    label = 'draalcore.auth'
    display_name = 'auth'

    def ready(self):
        from .actions import RegisterUserAction

        self.actions = [RegisterUserAction]
