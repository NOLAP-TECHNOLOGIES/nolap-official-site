from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from apps.accounts.views import home

urlpatterns = [
    path("", home, name="home"),
    path("", include("apps.accounts.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
]

if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
