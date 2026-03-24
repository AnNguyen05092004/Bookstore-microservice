from django.urls import path
from .views import (
    StaffList,
    StaffDetail,
    StaffLogin,
    StaffLogout,
    VerifyToken,
    HealthCheck,
)

urlpatterns = [
    # Staff profile CRUD
    path("staff/", StaffList.as_view(), name="staff-list"),
    path("staff/<uuid:staff_id>/", StaffDetail.as_view(), name="staff-detail"),
    # Staff auth and token validation
    path("login/", StaffLogin.as_view(), name="staff-login"),
    path("logout/", StaffLogout.as_view(), name="staff-logout"),
    path("verify/", VerifyToken.as_view(), name="verify-token"),
    # Service health endpoint
    path("health/", HealthCheck.as_view(), name="health-check"),
]
