from django.urls import include, path, re_path
from .api.views import CategoryTreeView, user_info
from .api.category_verification_views import CategoryVerificationViewSet
from .views import ReactAppView


urlpatterns = [
    path('user-info/', user_info, name='user_info'),
    path('categories/', CategoryTreeView.as_view(), name='category-tree'),
]



# React catch-all
urlpatterns += [
    re_path(r'^.*$', ReactAppView.as_view(), name='react-app'),
]