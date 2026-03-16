"""
Order Service - Models
Chuyển từ BookStore_Mono/bookstore/apps/orders/models.py
"""

import uuid
import hashlib
import time
from django.db import models


class Order(models.Model):
    """Order model"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.UUIDField()  # Reference to customer-service
    order_number = models.CharField(max_length=50, unique=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")

    # Pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Shipping address (cached)
    shipping_address = models.TextField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)

    # References to other services
    payment_id = models.UUIDField(blank=True, null=True)  # Reference to pay-service
    shipping_id = models.UUIDField(blank=True, null=True)  # Reference to ship-service

    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-order_date"]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            unique_str = f"{time.time()}{uuid.uuid4()}"
            self.order_number = (
                "ORD-" + hashlib.md5(unique_str.encode()).hexdigest()[:8].upper()
            )
        super().save(*args, **kwargs)

    def calculate_total(self):
        """Calculate order total"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total_amount = (
            self.subtotal - self.discount_amount + self.shipping_fee + self.tax_amount
        )
        self.save()
        return self.total_amount

    def update_status(self, new_status):
        """Update order status"""
        self.status = new_status
        self.save()


class OrderItem(models.Model):
    """Order Item model"""

    order_item_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book_id = models.UUIDField()  # Reference to book-service
    book_title = models.CharField(max_length=500, blank=True, null=True)  # Cached
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_item"
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.book_title} x {self.quantity}"

    def save(self, *args, **kwargs):
        from decimal import Decimal

        # Ensure unit_price is Decimal
        if isinstance(self.unit_price, str):
            self.unit_price = Decimal(self.unit_price)
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
