"""Ship Service - Views"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
import logging

from .models import Shipping
from .serializers import (
    ShippingSerializer,
    CreateShippingSerializer,
    UpdateShippingStatusSerializer,
    TrackingSerializer,
)

logger = logging.getLogger(__name__)
ORDER_SERVICE_URL = getattr(settings, "ORDER_SERVICE_URL", "http://order-service:8000")


class ShippingListCreate(APIView):
    """GET/POST shippings"""

    def get(self, request):
        order_id = request.query_params.get("order_id")
        if order_id:
            shippings = Shipping.objects.filter(order_id=order_id)
        else:
            shippings = Shipping.objects.all()
        return Response(ShippingSerializer(shippings, many=True).data)

    def post(self, request):
        serializer = CreateShippingSerializer(data=request.data)
        if serializer.is_valid():
            shipping = serializer.save()
            return Response(
                ShippingSerializer(shipping).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShippingDetail(APIView):
    """GET single shipping"""

    def get(self, request, shipping_id):
        shipping = get_object_or_404(Shipping, shipping_id=shipping_id)
        return Response(ShippingSerializer(shipping).data)


class UpdateShippingStatus(APIView):
    """PUT: Update shipping status"""

    def put(self, request, shipping_id):
        shipping = get_object_or_404(Shipping, shipping_id=shipping_id)
        serializer = UpdateShippingStatusSerializer(data=request.data)

        if serializer.is_valid():
            new_status = serializer.validated_data["status"]

            if new_status == "shipped":
                shipping.mark_shipped()
            elif new_status == "delivered":
                shipping.mark_delivered()
                # Update order status
                try:
                    requests.put(
                        f"{ORDER_SERVICE_URL}/orders/{shipping.order_id}/",
                        json={"status": "delivered"},
                        timeout=5,
                    )
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Error updating order: {e}")
            else:
                shipping.update_status(new_status)

            return Response(ShippingSerializer(shipping).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TrackShipping(APIView):
    """GET: Track shipping by tracking code"""

    def get(self, request, tracking_code):
        shipping = get_object_or_404(Shipping, tracking_code=tracking_code)
        tracking_data = {
            "tracking_code": shipping.tracking_code,
            "status": shipping.status,
            "carrier": shipping.carrier,
            "shipped_date": shipping.shipped_date,
            "estimated_delivery": shipping.estimated_delivery,
            "actual_delivery": shipping.actual_delivery,
        }
        return Response(tracking_data)


class HealthCheck(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "ship-service"})
