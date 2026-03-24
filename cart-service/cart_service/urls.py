"""
URL configuration for cart_service project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for cart-service
    path("admin/", admin.site.urls),
    # Cart domain APIs
    path("", include("app.urls")),
]
