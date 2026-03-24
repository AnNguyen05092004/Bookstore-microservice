from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for catalog-service
    path("admin/", admin.site.urls),
    # Catalog domain APIs
    path("", include("app.urls")),
]
