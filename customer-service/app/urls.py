"""
Customer Service - URLs
Theo mẫu từ PDF APPENDIX section 7.3.6
"""

from django.urls import path
from .views import (
    CustomerListCreate,
    CustomerDetail,
    CustomerLoyalty,
    HealthCheck,
    CustomerLogin,
    CustomerLogout,
)

urlpatterns = [
    # Customer CRUD and loyalty operations
    path("customers/", CustomerListCreate.as_view(), name="customer-list-create"),
    path(
        "customers/<uuid:customer_id>/",
        CustomerDetail.as_view(),
        name="customer-detail",
    ),
    path(
        "customers/<uuid:customer_id>/loyalty/",
        CustomerLoyalty.as_view(),
        name="customer-loyalty",
    ),
    # Customer authentication endpoints
    path("login/", CustomerLogin.as_view(), name="customer-login"),
    path("logout/", CustomerLogout.as_view(), name="customer-logout"),
    # Service health endpoint
    path("health/", HealthCheck.as_view(), name="health-check"),
]
