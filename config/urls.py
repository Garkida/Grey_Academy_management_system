"""
Root URL configuration for Grey Academy.

- /admin/            Django admin
- /accounts/         signup, login, logout, email verification, password reset
- /accounts/google/  Google OAuth login (provided by django-allauth)
- everything else    handled by the 'core' app (home, about, courses, dashboard...)
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    # path("accounts/", include("allauth.urls")), 
    # adds /accounts/google/login/ etc.
    path("api/", include("academy_api.urls")),
    path("", include("core.urls")),
    path("payments/", include("payments.urls")),
    path("attendance/", include("attendance.urls")),
    path("tutors/", include("tutors.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")
