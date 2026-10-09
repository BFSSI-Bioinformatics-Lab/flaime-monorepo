import json
from types import SimpleNamespace

import pytest
from django.test import RequestFactory

from flaime_py.food_labels.middleware import SuperuserErrorDetailsMiddleware


def _process(path, user):
    request = RequestFactory().get(path)
    request.user = user
    middleware = SuperuserErrorDetailsMiddleware(lambda request: None)
    try:
        raise ValueError("boom")
    except ValueError as exception:
        return middleware.process_exception(request, exception)


SUPERUSER = SimpleNamespace(is_superuser=True)
USER = SimpleNamespace(is_superuser=False)


@pytest.fixture()
def enabled(settings):
    settings.SHOW_ERRORS_TO_SUPERUSERS = True
    settings.URL_PREFIX = "/app/flaime"


def test_off_by_default(settings):
    settings.SHOW_ERRORS_TO_SUPERUSERS = False
    assert _process("/api/storeproducts/", SUPERUSER) is None


def test_api_error_returns_traceback_json(enabled):
    response = _process("/app/flaime/api/storeproducts/", SUPERUSER)
    body = json.loads(response.content)
    assert response.status_code == 500
    assert body["detail"] == "ValueError: boom"
    assert 'raise ValueError("boom")' in body["traceback"]


def test_page_error_returns_debug_page(enabled):
    response = _process("/app/flaime/admin/", SUPERUSER)
    assert response.status_code == 500
    assert response["Content-Type"].startswith("text/html")
    assert b"boom" in response.content


def test_not_shown_to_other_users(enabled):
    assert _process("/app/flaime/api/storeproducts/", USER) is None


def test_user_lookup_failure_falls_back_to_normal_500(enabled):
    class BrokenUser:
        @property
        def is_superuser(self):
            raise RuntimeError("database is down")

    assert _process("/app/flaime/api/storeproducts/", BrokenUser()) is None
