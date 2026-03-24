from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for ship-service
    path("admin/", admin.site.urls),
    # Shipping domain APIs
    path("", include("app.urls")),
]
