from draalcore.app_config import BaseAppConfig


class TestAppsConfig(BaseAppConfig):
    default = True
    name = 'draalcore.test_apps.test_models'
    label = 'test_models'
    verbose_name = 'Test apps models'
