from django.urls import path

from .views import (
    CustomerLoginAPI,
    StaffLoginAPI,
    VerifyTokenAPI,
    LogoutAPI,
    HealthCheck,
)


urlpatterns = [
    # Login APIs (customer/staff)
    path(
        "auth/customer/login/", CustomerLoginAPI.as_view(), name="auth-customer-login"
    ),
    path("auth/staff/login/", StaffLoginAPI.as_view(), name="auth-staff-login"),
    # JWT validation and logout APIs
    path("auth/verify/", VerifyTokenAPI.as_view(), name="auth-verify"),
    path("auth/logout/", LogoutAPI.as_view(), name="auth-logout"),
    # Service health endpoint
    path("health/", HealthCheck.as_view(), name="health-check"),
]
