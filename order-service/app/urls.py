from django.urls import path
from .views import OrderListCreate, OrderDetail, CancelOrder, HealthCheck

urlpatterns = [
    # Order CRUD and status APIs
    path("orders/", OrderListCreate.as_view(), name="order-list-create"),
    path("orders/<uuid:order_id>/", OrderDetail.as_view(), name="order-detail"),
    path("orders/<uuid:order_id>/cancel/", CancelOrder.as_view(), name="order-cancel"),
    # Service health endpoint
    path("health/", HealthCheck.as_view(), name="health-check"),
]
