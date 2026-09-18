import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "flaime_py.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import flaime_py.users.signals  # noqa: F401
