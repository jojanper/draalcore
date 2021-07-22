from draalcore.app_config import BaseAppConfig


class AuthConfig(BaseAppConfig):
    default = True
    name = 'draalcore.auth'
    label = 'draalcore_auth'
    display_name = 'auth'

    def ready(self):
        from .sites.actions import (GoogleExtAuthAction, FacebookExtAuthAction,
                                    TwitterExtAuthAction, OneDriveExtAuthAction,
                                    GoogleExtAuthCallbackAction, FacebookExtAuthCallbackAction,
                                    TwitterExtAuthCallbackAction, OneDriveExtAuthCallbackAction)

        from .authentication.actions import (LoginAction, LogoutAction, TokenAction,
                                             PasswordResetAction, PasswordResetConfirmAction,
                                             PasswordChangeAction, AuthUserDetailsAction)
        from .registration.actions import RegisterUserAction, ActivateUserAction

        # Authentication and user registration actions
        self.noauth_actions = [RegisterUserAction, ActivateUserAction,
                               LoginAction, LogoutAction, TokenAction,
                               PasswordResetAction, PasswordResetConfirmAction,
                               GoogleExtAuthAction, FacebookExtAuthAction,
                               TwitterExtAuthAction, OneDriveExtAuthAction,
                               GoogleExtAuthCallbackAction, FacebookExtAuthCallbackAction,
                               TwitterExtAuthCallbackAction, OneDriveExtAuthCallbackAction]

        # Actions requiring authentication
        self.actions = [PasswordChangeAction, AuthUserDetailsAction]
