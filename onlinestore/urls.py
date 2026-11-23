"""
URL configuration for onlinestore project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


def home(request):
    """Главная страница - перенаправление на каталог."""
    from django.shortcuts import redirect
    return redirect("store:product_list")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("store/", include("store.urls")),
    path("users/", include("users.urls")),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
