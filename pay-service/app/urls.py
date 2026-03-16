from django.urls import path
from .views import (
    PaymentListCreate,
    PaymentDetail,
    ProcessPayment,
    RefundPayment,
    HealthCheck,
)

urlpatterns = [
    path("payments/", PaymentListCreate.as_view(), name="payment-list-create"),
    path("payments/<uuid:payment_id>/", PaymentDetail.as_view(), name="payment-detail"),
    path(
        "payments/<uuid:payment_id>/process/",
        ProcessPayment.as_view(),
        name="process-payment",
    ),
    path("refunds/", RefundPayment.as_view(), name="refund-payment"),
    path("health/", HealthCheck.as_view(), name="health-check"),
]
