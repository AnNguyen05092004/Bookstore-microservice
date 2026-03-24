"""
URL configuration for book_service project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for book-service
    path("admin/", admin.site.urls),
    # Book domain APIs
    path("", include("app.urls")),
]
