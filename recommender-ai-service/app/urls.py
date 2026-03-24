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
    # User behaviour tracking API
    path("behaviours/", TrackBehaviour.as_view(), name="track-behaviour"),
    # Recommendation query APIs
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
    # Recommendation engine management API
    path("engines/", EngineList.as_view(), name="engine-list"),
    # Service health endpoint
    path("health/", HealthCheck.as_view(), name="health-check"),
]
