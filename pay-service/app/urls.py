from django.urls import path
from .views import (
    PaymentListCreate,
    PaymentDetail,
    ProcessPayment,
    RefundPayment,
    HealthCheck,
)

urlpatterns = [
    # Payment CRUD and processing APIs
    path("payments/", PaymentListCreate.as_view(), name="payment-list-create"),
    path("payments/<uuid:payment_id>/", PaymentDetail.as_view(), name="payment-detail"),
    path(
        "payments/<uuid:payment_id>/process/",
        ProcessPayment.as_view(),
        name="process-payment",
    ),
    # Refund API
    path("refunds/", RefundPayment.as_view(), name="refund-payment"),
    # Service health endpoint
    path("health/", HealthCheck.as_view(), name="health-check"),
]
