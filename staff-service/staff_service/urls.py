from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for staff-service
    path("admin/", admin.site.urls),
    # Staff management APIs
    path("", include("app.urls")),
]
