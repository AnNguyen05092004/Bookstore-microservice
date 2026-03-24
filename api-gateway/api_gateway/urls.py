from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for gateway service
    path("admin/", admin.site.urls),
    # Public web pages + API proxy routes
    path("", include("app.urls")),
]
