"""Staff Service - Views"""

import hashlib
import secrets
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Staff, StaffSession
from .serializers import (
    StaffSerializer,
    StaffCreateSerializer,
    StaffLoginSerializer,
    StaffSessionSerializer,
)


class StaffList(APIView):
    """GET: List all staff, POST: Create new staff"""

    def get(self, request):
        role = request.query_params.get("role")
        department = request.query_params.get("department")
        include_inactive = (
            request.query_params.get("include_inactive", "false").lower() == "true"
        )

        staff = (
            Staff.objects.all()
            if include_inactive
            else Staff.objects.filter(is_active=True)
        )

        if role:
            staff = staff.filter(role=role)
        if department:
            staff = staff.filter(department__icontains=department)

        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StaffCreateSerializer(data=request.data)
        if serializer.is_valid():
            staff = serializer.save()
            return Response(StaffSerializer(staff).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffDetail(APIView):
    """GET/PUT/DELETE staff by ID"""

    def get(self, request, staff_id):
        staff = get_object_or_404(Staff, staff_id=staff_id)
        return Response(StaffSerializer(staff).data)

    def put(self, request, staff_id):
        staff = get_object_or_404(Staff, staff_id=staff_id)
        serializer = StaffSerializer(staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, staff_id):
        staff = get_object_or_404(Staff, staff_id=staff_id)
        allowed_fields = {"is_active", "role", "department"}
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        serializer = StaffSerializer(staff, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, staff_id):
        staff = get_object_or_404(Staff, staff_id=staff_id)
        staff.is_active = False
        staff.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffLogin(APIView):
    """POST: Staff login authentication"""

    def post(self, request):
        serializer = StaffLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            try:
                staff = Staff.objects.get(
                    email=email, password_hash=password_hash, is_active=True
                )
            except Staff.DoesNotExist:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Create session
            token = secrets.token_urlsafe(64)
            session = StaffSession.objects.create(
                staff=staff,
                token=token,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                expires_at=timezone.now() + timedelta(hours=8),
            )

            staff.last_login = timezone.now()
            staff.save()

            return Response(
                {
                    "token": token,
                    "staff": StaffSerializer(staff).data,
                    "expires_at": session.expires_at,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffLogout(APIView):
    """POST: Staff logout"""

    def post(self, request):
        token = request.data.get("token")
        if token:
            StaffSession.objects.filter(token=token).update(is_active=False)
        return Response({"message": "Logged out successfully"})


class VerifyToken(APIView):
    """POST: Verify staff token"""

    def post(self, request):
        token = request.data.get("token")

        try:
            session = StaffSession.objects.get(
                token=token, is_active=True, expires_at__gt=timezone.now()
            )
            return Response(
                {"valid": True, "staff": StaffSerializer(session.staff).data}
            )
        except StaffSession.DoesNotExist:
            return Response({"valid": False}, status=status.HTTP_401_UNAUTHORIZED)


class HealthCheck(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "staff-service"})
