"""
Cart Service - URLs
"""

from django.urls import path
from .views import (
    CartCreate,
    CartDetail,
    AddCartItem,
    UpdateCartItem,
    ClearCart,
    HealthCheck,
)

urlpatterns = [
    path("carts/", CartCreate.as_view(), name="cart-create"),
    path("carts/<uuid:customer_id>/", CartDetail.as_view(), name="cart-detail"),
    path(
        "carts/<uuid:customer_id>/items/", AddCartItem.as_view(), name="add-cart-item"
    ),
    path(
        "carts/<uuid:customer_id>/items/<uuid:book_id>/",
        UpdateCartItem.as_view(),
        name="update-cart-item",
    ),
    path("carts/<uuid:customer_id>/clear/", ClearCart.as_view(), name="clear-cart"),
    path("health/", HealthCheck.as_view(), name="health-check"),
]
