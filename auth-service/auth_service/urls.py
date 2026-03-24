from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for auth-service
    path("admin/", admin.site.urls),
    # Central authentication APIs
    path("", include("app.urls")),
]
