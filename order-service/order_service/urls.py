from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for order-service
    path("admin/", admin.site.urls),
    # Order domain APIs
    path("", include("app.urls")),
]
