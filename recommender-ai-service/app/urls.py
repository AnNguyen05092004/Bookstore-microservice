from django.urls import path
from .views import (
    TrackBehaviour,
    GetRecommendations,
    PopularBooks,
    CustomerHistory,
    EngineList,
    HealthCheck,
)

urlpatterns = [
    path("behaviours/", TrackBehaviour.as_view(), name="track-behaviour"),
    path(
        "recommendations/<uuid:customer_id>/",
        GetRecommendations.as_view(),
        name="get-recommendations",
    ),
    path("popular/", PopularBooks.as_view(), name="popular-books"),
    path(
        "history/<uuid:customer_id>/",
        CustomerHistory.as_view(),
        name="customer-history",
    ),
    path("engines/", EngineList.as_view(), name="engine-list"),
    path("health/", HealthCheck.as_view(), name="health-check"),
]
