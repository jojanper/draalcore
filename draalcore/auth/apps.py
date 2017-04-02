from draalcore.app_config import BaseAppConfig


class AuthConfig(BaseAppConfig):
    name = 'draalcore.auth'
    label = 'draalcore.auth'
    display_name = 'auth'

    def ready(self):
        from .registration.actions import RegisterUserAction

        self.noauth_actions = [RegisterUserAction]
