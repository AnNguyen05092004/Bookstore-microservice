"""
Cart Service - Views
Theo mẫu từ PDF APPENDIX section 7.5.3
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
import logging

from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    CartCreateSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
)

logger = logging.getLogger(__name__)

BOOK_SERVICE_URL = getattr(settings, "BOOK_SERVICE_URL", "http://book-service:8000")


class CartCreate(APIView):
    """
    GET: Lấy danh sách tất cả carts
    POST: Tạo cart mới cho customer
    """

    def get(self, request):
        carts = Cart.objects.filter(is_active=True)
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CartCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Check if customer already has active cart
            customer_id = serializer.validated_data["customer_id"]
            existing_cart = Cart.objects.filter(
                customer_id=customer_id, is_active=True
            ).first()

            if existing_cart:
                return Response(
                    CartSerializer(existing_cart).data, status=status.HTTP_200_OK
                )

            cart = serializer.save()
            return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartDetail(APIView):
    """
    GET: Lấy cart của customer (tự tạo nếu chưa có)
    DELETE: Xóa cart
    """

    def get(self, request, customer_id):
        # Auto-create cart if not exists
        cart, created = Cart.objects.get_or_create(
            customer_id=customer_id, is_active=True
        )
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request, customer_id):
        cart = get_object_or_404(Cart, customer_id=customer_id, is_active=True)
        cart.is_active = False
        cart.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddCartItem(APIView):
    """
    POST: Thêm sách vào cart
    Kiểm tra sách tồn tại từ book-service trước khi thêm
    Tự động tạo cart nếu chưa có
    """

    def post(self, request, customer_id):
        # Auto-create cart if not exists
        cart, created = Cart.objects.get_or_create(
            customer_id=customer_id, is_active=True
        )
        serializer = AddCartItemSerializer(data=request.data)

        if serializer.is_valid():
            book_id = serializer.validated_data["book_id"]
            quantity = serializer.validated_data["quantity"]

            # Gọi book-service để kiểm tra sách tồn tại và lấy thông tin
            try:
                book_response = requests.get(
                    f"{BOOK_SERVICE_URL}/books/{book_id}/", timeout=5
                )

                if book_response.status_code != 200:
                    return Response(
                        {"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND
                    )

                book_data = book_response.json()

                # Kiểm tra stock
                if book_data.get("stock_quantity", 0) < quantity:
                    return Response(
                        {"error": "Insufficient stock"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            except requests.exceptions.RequestException as e:
                logger.error(f"Error calling book-service: {e}")
                return Response(
                    {"error": "Unable to verify book"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            # Thêm hoặc cập nhật cart item
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                book_id=book_id,
                defaults={
                    "quantity": quantity,
                    "unit_price": book_data.get("price", 0),
                    "book_title": book_data.get("title", ""),
                },
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response(
                CartItemSerializer(cart_item).data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateCartItem(APIView):
    """
    PUT: Cập nhật số lượng item trong cart
    DELETE: Xóa item khỏi cart
    """

    def put(self, request, customer_id, book_id):
        cart = get_object_or_404(Cart, customer_id=customer_id, is_active=True)
        cart_item = get_object_or_404(CartItem, cart=cart, book_id=book_id)

        serializer = UpdateCartItemSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data["quantity"]

            if quantity == 0:
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            cart_item.update_quantity(quantity)
            return Response(CartItemSerializer(cart_item).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, customer_id, book_id):
        cart = get_object_or_404(Cart, customer_id=customer_id, is_active=True)
        cart_item = get_object_or_404(CartItem, cart=cart, book_id=book_id)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClearCart(APIView):
    """
    POST: Xóa tất cả items trong cart
    """

    def post(self, request, customer_id):
        cart = get_object_or_404(Cart, customer_id=customer_id, is_active=True)
        cart.clear()
        return Response(CartSerializer(cart).data)


class HealthCheck(APIView):
    """Health check endpoint"""

    def get(self, request):
        return Response({"status": "healthy", "service": "cart-service"})
