"""
Pay Service - Models
Chuyển từ BookStore_Mono/bookstore/apps/payments/models.py
"""

import uuid
from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """Payment model"""

    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("card", "Credit/Debit Card"),
        ("bank_transfer", "Bank Transfer"),
        ("e_wallet", "E-Wallet"),
        ("cod", "Cash on Delivery"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.UUIDField()  # Reference to order-service
    payment_method = models.CharField(
        max_length=50, choices=METHOD_CHOICES, default="cod"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="VND")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment"
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment {self.payment_id} - {self.status}"

    def complete_payment(self):
        """Complete payment"""
        self.status = "completed"
        self.paid_at = timezone.now()
        self.save()

    def fail_payment(self):
        """Mark payment as failed"""
        self.status = "failed"
        self.save()

    def refund(self):
        """Refund payment"""
        self.status = "refunded"
        self.save()


class PaymentTransaction(models.Model):
    """Payment Transaction log"""

    transaction_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="transactions"
    )
    gateway = models.CharField(max_length=100, blank=True, null=True)
    gateway_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    response_code = models.CharField(max_length=50, blank=True, null=True)
    response_message = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    transaction_time = models.DateTimeField(auto_now_add=True)
    raw_response = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "payment_transaction"

    def __str__(self):
        return f"Transaction {self.transaction_id}"


class Refund(models.Model):
    """Refund model"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    ]

    refund_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="refunds"
    )
    order_id = models.UUIDField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    processed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "refund"

    def __str__(self):
        return f"Refund {self.refund_id}"
