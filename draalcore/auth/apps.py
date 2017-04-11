from draalcore.app_config import BaseAppConfig


class AuthConfig(BaseAppConfig):
    name = 'draalcore.auth'
    label = 'draalcore.auth'
    display_name = 'auth'

    def ready(self):
        from .authentication.actions import LoginAction, LogoutAction, TokenAction
        from .registration.actions import RegisterUserAction, ActivateUserAction

        # Authentication and user registration actions
        self.noauth_actions = [RegisterUserAction, ActivateUserAction,
            LoginAction, LogoutAction, TokenAction]
