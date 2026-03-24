"""Order Service - Views"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
import logging

from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    CreateOrderSerializer,
    UpdateOrderStatusSerializer,
)

logger = logging.getLogger(__name__)

CART_SERVICE_URL = getattr(settings, "CART_SERVICE_URL", "http://cart-service:8000")
BOOK_SERVICE_URL = getattr(settings, "BOOK_SERVICE_URL", "http://book-service:8000")
PAY_SERVICE_URL = getattr(settings, "PAY_SERVICE_URL", "http://pay-service:8000")
SHIP_SERVICE_URL = getattr(settings, "SHIP_SERVICE_URL", "http://ship-service:8000")


def _sync_book_sales_for_order(order, multiplier=1):
    """Sync sold counters in book-service based on order items."""
    for item in order.items.all():
        try:
            requests.post(
                f"{BOOK_SERVICE_URL}/books/{item.book_id}/sales/",
                json={
                    "quantity": int(item.quantity or 0) * int(multiplier),
                    "mode": "increment",
                },
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            logger.warning(
                "Error syncing sold count for book %s in order %s: %s",
                item.book_id,
                order.order_id,
                e,
            )


def _apply_sales_transition(order, previous_status, new_status):
    """
    Sales rule:
    - Count sales for every non-cancelled/non-refunded order.
    - Decrement when transitioning into cancelled/refunded.
    - Re-increment when transitioning out of cancelled/refunded.
    """
    old_cancelled = previous_status in {"cancelled", "refunded"}
    new_cancelled = new_status in {"cancelled", "refunded"}

    if not old_cancelled and new_cancelled:
        _sync_book_sales_for_order(order, multiplier=-1)
    elif old_cancelled and not new_cancelled:
        _sync_book_sales_for_order(order, multiplier=1)


class OrderListCreate(APIView):
    """
    GET: Lấy danh sách orders
    POST: Tạo order từ cart
    """

    def get(self, request):
        customer_id = request.query_params.get("customer_id")
        if customer_id:
            orders = Order.objects.filter(customer_id=customer_id)
        else:
            orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        customer_id = serializer.validated_data["customer_id"]

        # 1. Lấy cart từ cart-service
        try:
            cart_response = requests.get(
                f"{CART_SERVICE_URL}/carts/{customer_id}/", timeout=5
            )
            if cart_response.status_code != 200:
                return Response(
                    {"error": "Cart not found or empty"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            cart_data = cart_response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling cart-service: {e}")
            return Response(
                {"error": "Unable to fetch cart"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if not cart_data.get("items"):
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Tạo Order
        order = Order.objects.create(
            customer_id=customer_id,
            subtotal=cart_data.get("total", 0),
            total_amount=cart_data.get("total", 0),
            shipping_address=serializer.validated_data.get("shipping_address", ""),
            billing_address=serializer.validated_data.get("billing_address", ""),
            notes=serializer.validated_data.get("notes", ""),
        )

        # 3. Tạo OrderItems từ cart items
        for cart_item in cart_data.get("items", []):
            OrderItem.objects.create(
                order=order,
                book_id=cart_item["book_id"],
                book_title=cart_item.get("book_title", ""),
                quantity=cart_item["quantity"],
                unit_price=cart_item["unit_price"],
            )

        # Count as sold immediately after order creation.
        _sync_book_sales_for_order(order, multiplier=1)

        # 4. Gọi pay-service để tạo payment
        try:
            payment_response = requests.post(
                f"{PAY_SERVICE_URL}/payments/",
                json={
                    "order_id": str(order.order_id),
                    "amount": float(order.total_amount),
                    "payment_method": serializer.validated_data.get(
                        "payment_method", "cod"
                    ),
                },
                timeout=5,
            )
            if payment_response.status_code == 201:
                payment_data = payment_response.json()
                order.payment_id = payment_data.get("payment_id")
                order.save()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error calling pay-service: {e}")

        # 5. Gọi ship-service để tạo shipping
        try:
            ship_response = requests.post(
                f"{SHIP_SERVICE_URL}/shippings/",
                json={
                    "order_id": str(order.order_id),
                    "shipping_method": serializer.validated_data.get(
                        "shipping_method", "standard"
                    ),
                    "shipping_address": order.shipping_address,
                },
                timeout=5,
            )
            if ship_response.status_code == 201:
                ship_data = ship_response.json()
                order.shipping_id = ship_data.get("shipping_id")
                from decimal import Decimal

                fee = ship_data.get("fee", 0)
                order.shipping_fee = Decimal(str(fee)) if fee else Decimal("0")
                order.save()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error calling ship-service: {e}")

        # 6. Clear cart sau khi tạo order thành công
        try:
            requests.post(f"{CART_SERVICE_URL}/carts/{customer_id}/clear/", timeout=5)
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error clearing cart: {e}")

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetail(APIView):
    """GET/PUT/DELETE single order"""

    def get(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)
        return Response(OrderSerializer(order).data)

    def put(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)
        previous_status = str(order.status or "").lower()
        serializer = UpdateOrderStatusSerializer(data=request.data)
        if serializer.is_valid():
            new_status = str(serializer.validated_data["status"] or "").lower()
            order.update_status(new_status)

            _apply_sales_transition(order, previous_status, new_status)

            return Response(OrderSerializer(order).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)
        if order.status not in ["pending", "cancelled"]:
            return Response(
                {"error": "Cannot delete order in this status"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CancelOrder(APIView):
    """POST: Cancel order"""

    def post(self, request, order_id):
        order = get_object_or_404(Order, order_id=order_id)
        if order.status not in ["pending", "confirmed"]:
            return Response(
                {"error": "Cannot cancel order in this status"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        previous_status = str(order.status or "").lower()
        order.update_status("cancelled")
        _apply_sales_transition(order, previous_status, "cancelled")
        return Response(OrderSerializer(order).data)


class HealthCheck(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "order-service"})
