from django.urls import path
from .views import (
    ShippingListCreate,
    ShippingDetail,
    UpdateShippingStatus,
    TrackShipping,
    HealthCheck,
)

urlpatterns = [
    path("shippings/", ShippingListCreate.as_view(), name="shipping-list-create"),
    path(
        "shippings/<uuid:shipping_id>/",
        ShippingDetail.as_view(),
        name="shipping-detail",
    ),
    path(
        "shippings/<uuid:shipping_id>/status/",
        UpdateShippingStatus.as_view(),
        name="update-shipping-status",
    ),
    path("track/<str:tracking_code>/", TrackShipping.as_view(), name="track-shipping"),
    path("health/", HealthCheck.as_view(), name="health-check"),
]
