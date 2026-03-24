from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin for recommender service
    path("admin/", admin.site.urls),
    # Recommendation and behaviour APIs
    path("", include("app.urls")),
]
