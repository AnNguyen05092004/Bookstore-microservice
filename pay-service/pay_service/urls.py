from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for pay-service
    path("admin/", admin.site.urls),
    # Payment domain APIs
    path("", include("app.urls")),
]
