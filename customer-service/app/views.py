"""
Customer Service - Views
Theo mẫu từ PDF APPENDIX section 7.3.5
"""

import hashlib
import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
import logging

from .models import Customer
from .serializers import (
    CustomerSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer,
)

logger = logging.getLogger(__name__)

CART_SERVICE_URL = getattr(settings, "CART_SERVICE_URL", "http://cart-service:8000")


class CustomerListCreate(APIView):
    """
    GET: Lấy danh sách tất cả customers
    POST: Tạo customer mới + tự động tạo cart (gọi cart-service)
    """

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerCreateSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()

            # Gọi cart-service để tự động tạo cart cho customer mới
            try:
                cart_response = requests.post(
                    f"{CART_SERVICE_URL}/carts/",
                    json={"customer_id": str(customer.customer_id)},
                    timeout=5,
                )
                if cart_response.status_code == 201:
                    logger.info(f"Cart created for customer {customer.customer_id}")
                else:
                    logger.warning(
                        f"Failed to create cart for customer {customer.customer_id}"
                    )
            except requests.exceptions.RequestException as e:
                logger.error(f"Error calling cart-service: {e}")

            return Response(
                CustomerSerializer(customer).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetail(APIView):
    """
    GET: Lấy thông tin 1 customer
    PUT: Cập nhật thông tin customer
    DELETE: Xóa customer
    """

    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def put(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        serializer = CustomerUpdateSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(CustomerSerializer(customer).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerLoyalty(APIView):
    """
    POST: Thêm loyalty points cho customer
    """

    def post(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        points = request.data.get("points", 0)

        if points <= 0:
            return Response(
                {"error": "Points must be positive"}, status=status.HTTP_400_BAD_REQUEST
            )

        customer.add_loyalty_points(points)
        return Response(
            {
                "customer_id": str(customer.customer_id),
                "loyalty_points": customer.loyalty_points,
                "tier": customer.tier,
            }
        )


class HealthCheck(APIView):
    """Health check endpoint"""

    def get(self, request):
        return Response({"status": "healthy", "service": "customer-service"})


class CustomerLogin(APIView):
    """POST: Customer login"""

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            customer = Customer.objects.get(email=email, is_active=True)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Simple password check (in production, use proper hashing)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if (
            customer.password_hash != password_hash
            and customer.password_hash != password
        ):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        # Generate token
        token = secrets.token_urlsafe(32)

        return Response(
            {
                "token": token,
                "customer": CustomerSerializer(customer).data,
            }
        )


class CustomerLogout(APIView):
    """POST: Customer logout"""

    def post(self, request):
        return Response({"message": "Logged out successfully"})
