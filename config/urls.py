# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path, re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from food_labels.views import ReactAppView
from flaime_py.food_labels.api.views import get_search_options


# Path prefix this app is served under behind FSDH's path-based reverse proxy
# (e.g. "/app/flaime"), which forwards the full incoming path rather than
# stripping it. FORCE_SCRIPT_NAME alone only affects reverse()/absolute-URL
# generation, not routing, so the prefix has to be baked into the patterns
# themselves for incoming requests to match. Empty string for local dev.
PREFIX = f"{settings.URL_PREFIX.strip('/')}/" if settings.URL_PREFIX else ""

urlpatterns = [
    path(
        f"{PREFIX}about/",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(f"{PREFIX}{settings.ADMIN_URL}", admin.site.urls),
    # User management
    path(f"{PREFIX}users/", include("flaime_py.users.urls", namespace="users")),
    path(f"{PREFIX}accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    # ...
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

# API URLS
urlpatterns += [
    path(f"{PREFIX}api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        f"{PREFIX}api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path(f"{PREFIX}api/token-auth/", csrf_exempt(obtain_auth_token), name="api_token_auth"),
    path(f"{PREFIX}api/options/", get_search_options, name="search_options"),
    path(f"{PREFIX}api/", include("config.api_router")),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            f"{PREFIX}400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            f"{PREFIX}403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            f"{PREFIX}404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path(f"{PREFIX}500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path(f"{PREFIX}__debug__/", include(debug_toolbar.urls))] + urlpatterns


# React catch-all
urlpatterns += [
    re_path(rf"^{PREFIX}.*$", ReactAppView.as_view(), name="home"),
]
