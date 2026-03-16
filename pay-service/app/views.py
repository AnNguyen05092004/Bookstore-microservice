"""Pay Service - Views"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
import requests
import logging

from .models import Payment, PaymentTransaction, Refund
from .serializers import (
    PaymentSerializer,
    CreatePaymentSerializer,
    RefundSerializer,
    CreateRefundSerializer,
)

logger = logging.getLogger(__name__)
ORDER_SERVICE_URL = getattr(settings, "ORDER_SERVICE_URL", "http://order-service:8000")


class PaymentListCreate(APIView):
    """GET/POST payments"""

    def get(self, request):
        order_id = request.query_params.get("order_id")
        if order_id:
            payments = Payment.objects.filter(order_id=order_id)
        else:
            payments = Payment.objects.all()
        return Response(PaymentSerializer(payments, many=True).data)

    def post(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()

            # Log transaction
            PaymentTransaction.objects.create(
                payment=payment,
                gateway=payment.payment_method,
                response_code="INITIATED",
                response_message="Payment initiated",
                amount=payment.amount,
            )

            return Response(
                PaymentSerializer(payment).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentDetail(APIView):
    """GET single payment"""

    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, payment_id=payment_id)
        return Response(PaymentSerializer(payment).data)


class ProcessPayment(APIView):
    """POST: Process/Complete payment"""

    def post(self, request, payment_id):
        payment = get_object_or_404(Payment, payment_id=payment_id)

        if payment.status != "pending":
            return Response(
                {"error": f"Cannot process payment with status {payment.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Simulate payment processing
        payment.complete_payment()

        # Log transaction
        PaymentTransaction.objects.create(
            payment=payment,
            gateway=payment.payment_method,
            response_code="SUCCESS",
            response_message="Payment completed successfully",
            amount=payment.amount,
        )

        # Update order status
        try:
            requests.put(
                f"{ORDER_SERVICE_URL}/orders/{payment.order_id}/",
                json={"status": "confirmed"},
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error updating order status: {e}")

        return Response(PaymentSerializer(payment).data)


class RefundPayment(APIView):
    """POST: Request refund"""

    def post(self, request):
        serializer = CreateRefundSerializer(data=request.data)
        if serializer.is_valid():
            payment = get_object_or_404(
                Payment, payment_id=serializer.validated_data["payment_id"]
            )

            if payment.status != "completed":
                return Response(
                    {"error": "Can only refund completed payments"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            refund = Refund.objects.create(
                payment=payment,
                order_id=payment.order_id,
                amount=serializer.validated_data["amount"],
                reason=serializer.validated_data.get("reason", ""),
            )

            return Response(
                RefundSerializer(refund).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthCheck(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "pay-service"})
