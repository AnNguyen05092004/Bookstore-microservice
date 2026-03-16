"""
Ship Service - Models
Chuyển từ BookStore_Mono/bookstore/apps/shipping/models.py
"""

import uuid
import hashlib
import time
from django.db import models


class Shipping(models.Model):
    """Shipping model"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
    ]

    METHOD_CHOICES = [
        ("standard", "Standard Delivery"),
        ("express", "Express Delivery"),
        ("same_day", "Same Day Delivery"),
    ]

    shipping_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.UUIDField()  # Reference to order-service
    shipping_method = models.CharField(
        max_length=100, choices=METHOD_CHOICES, default="standard"
    )
    carrier = models.CharField(max_length=100, blank=True, null=True)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    shipping_address = models.TextField(blank=True, null=True)
    tracking_code = models.CharField(max_length=255, blank=True, null=True)
    shipped_date = models.DateTimeField(blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)
    actual_delivery = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipping"
        verbose_name = "Shipping"
        verbose_name_plural = "Shippings"

    def __str__(self):
        return f"Shipping {self.shipping_id}"

    def save(self, *args, **kwargs):
        if not self.fee:
            self.calculate_fee()
        if not self.tracking_code:
            self.generate_tracking_code()
        super().save(*args, **kwargs)

    def calculate_fee(self):
        """Calculate shipping fee based on method"""
        fee_map = {
            "standard": 25000,
            "express": 50000,
            "same_day": 100000,
        }
        self.fee = fee_map.get(self.shipping_method, 25000)
        return self.fee

    def generate_tracking_code(self):
        """Generate unique tracking code"""
        unique_str = f"{self.shipping_id}{time.time()}"
        self.tracking_code = (
            "TRK-" + hashlib.md5(unique_str.encode()).hexdigest()[:10].upper()
        )
        return self.tracking_code

    def mark_shipped(self):
        """Mark as shipped"""
        from django.utils import timezone

        self.shipped_date = timezone.now()
        self.status = "shipped"
        self.save()

    def mark_delivered(self):
        """Mark as delivered"""
        from django.utils import timezone

        self.actual_delivery = timezone.now()
        self.status = "delivered"
        self.save()

    def update_status(self, new_status):
        self.status = new_status
        self.save()
