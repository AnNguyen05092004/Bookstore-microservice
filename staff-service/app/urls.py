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
    path("staff/", StaffList.as_view(), name="staff-list"),
    path("staff/<uuid:staff_id>/", StaffDetail.as_view(), name="staff-detail"),
    path("login/", StaffLogin.as_view(), name="staff-login"),
    path("logout/", StaffLogout.as_view(), name="staff-logout"),
    path("verify/", VerifyToken.as_view(), name="verify-token"),
    path("health/", HealthCheck.as_view(), name="health-check"),
]
