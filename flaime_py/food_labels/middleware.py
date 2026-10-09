import logging
import traceback

from django.conf import settings
from django.http import JsonResponse
from django.views.debug import technical_500_response

logger = logging.getLogger(__name__)


class SuperuserErrorDetailsMiddleware:
    """Show superusers the traceback of an unhandled exception.

    Off unless DJANGO_SHOW_ERRORS_TO_SUPERUSERS is set. Meant for debugging a
    deployment whose server logs can't be read: API requests get the traceback
    in the JSON body (which the frontend prints to the browser console), other
    pages get Django's debug error page. Everyone else still gets the normal
    500 page, and the exception is logged either way.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if not settings.SHOW_ERRORS_TO_SUPERUSERS or not _is_superuser(request):
            return None
        logger.error("Internal Server Error: %s", request.path, exc_info=exception)
        if request.path.startswith(f"{settings.URL_PREFIX}/api/"):
            return JsonResponse(
                {
                    "detail": f"{type(exception).__name__}: {exception}",
                    "traceback": "".join(traceback.format_exception(exception)),
                },
                status=500,
            )
        return technical_500_response(request, type(exception), exception, exception.__traceback__)


def _is_superuser(request):
    # The exception may have come from the database, in which case loading
    # the user can fail too.
    try:
        return request.user.is_superuser
    except Exception:  # noqa: BLE001
        return False
