from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for comment-rate-service
    path("admin/", admin.site.urls),
    # Review/rating domain APIs
    path("", include("app.urls")),
]
