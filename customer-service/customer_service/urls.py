"""
URL configuration for customer_service project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for customer-service
    path("admin/", admin.site.urls),
    # Customer domain APIs
    path("", include("app.urls")),
]
