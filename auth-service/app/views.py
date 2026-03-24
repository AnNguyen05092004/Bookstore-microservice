"""Auth Service - JWT login + token verification"""

from datetime import datetime, timedelta, timezone

import jwt
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


def _service_login(service_url, email, password):
    try:
        resp = requests.post(
            f"{service_url}/login/",
            json={"email": email, "password": password},
            timeout=10,
        )
    except requests.RequestException as exc:
        return {"error": str(exc)}, status.HTTP_503_SERVICE_UNAVAILABLE
    try:
        data = resp.json() if resp.content else {}
    except ValueError:
        data = {}
    return data, resp.status_code


def _issue_token(payload):
    now = datetime.now(timezone.utc)
    claims = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=settings.JWT_EXPIRES_HOURS)).timestamp()),
    }
    token = jwt.encode(claims, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, claims


class CustomerLoginAPI(APIView):
    """Central customer login -> returns JWT + customer profile"""

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data, status_code = _service_login(
            settings.CUSTOMER_SERVICE_URL, email, password
        )
        if status_code != status.HTTP_200_OK or not data.get("customer"):
            return Response(data, status=status_code)

        customer = data["customer"]
        token, claims = _issue_token(
            {
                "sub": str(customer.get("customer_id") or ""),
                "user_type": "customer",
                "role": "customer",
                "name": customer.get("full_name") or customer.get("first_name") or "",
                "email": customer.get("email") or email,
            }
        )
        return Response({"token": token, "customer": customer, "claims": claims})


class StaffLoginAPI(APIView):
    """Central staff/manager login -> returns JWT + staff profile"""

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        portal = (request.data.get("portal") or "staff").lower()
        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data, status_code = _service_login(settings.STAFF_SERVICE_URL, email, password)
        if status_code != status.HTTP_200_OK or not data.get("staff"):
            return Response(data, status=status_code)

        staff = data["staff"]
        role = (staff.get("role") or "staff").lower()
        is_manager = role in {"manager", "admin"}

        if portal == "manager" and not is_manager:
            return Response(
                {
                    "error": "Only manager/admin can access manager portal",
                    "staff": staff,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if portal == "staff" and is_manager:
            return Response(
                {
                    "error": "Manager/Admin account must login via /manager/login/",
                    "staff": staff,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        token, claims = _issue_token(
            {
                "sub": str(staff.get("staff_id") or ""),
                "user_type": "staff",
                "role": role,
                "name": staff.get("first_name") or "",
                "email": staff.get("email") or email,
            }
        )
        return Response({"token": token, "staff": staff, "claims": claims})


class VerifyTokenAPI(APIView):
    """Verify JWT and optionally enforce role list"""

    def post(self, request):
        token = request.data.get("token")
        required_roles = request.data.get("required_roles") or []
        if not token:
            return Response(
                {"valid": False, "error": "Missing token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            claims = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            return Response(
                {"valid": False, "error": "Token expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.InvalidTokenError:
            return Response(
                {"valid": False, "error": "Invalid token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        role = (claims.get("role") or "").lower()
        allowed = {str(r).lower() for r in required_roles if str(r).strip()}
        if allowed and role not in allowed:
            return Response(
                {"valid": False, "error": "Forbidden role", "claims": claims},
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response({"valid": True, "claims": claims})


class LogoutAPI(APIView):
    """Stateless JWT logout placeholder (client removes token)"""

    def post(self, request):
        return Response({"success": True})


class HealthCheck(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "auth-service"})
