"""
Cart Service - Models
Chuyển từ BookStore_Mono/bookstore/apps/cart/models.py
"""

import uuid
from django.db import models
from decimal import Decimal


class Cart(models.Model):
    """Shopping Cart model"""

    cart_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.UUIDField()  # Reference to customer-service
    session_id = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "cart"
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart {self.cart_id} - Customer {self.customer_id}"

    def calculate_total(self):
        """Calculate cart total"""
        return sum(item.calculate_subtotal() for item in self.items.all())

    def get_item_count(self):
        """Get total number of items in cart"""
        return self.items.aggregate(total=models.Sum("quantity"))["total"] or 0

    def clear(self):
        """Clear all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Cart Item model"""

    cart_item_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book_id = models.UUIDField()  # Reference to book-service
    book_title = models.CharField(
        max_length=500, blank=True, null=True
    )  # Cached from book-service
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_item"
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ("cart", "book_id")

    def __str__(self):
        return f"{self.book_title or self.book_id} x {self.quantity}"

    def update_quantity(self, qty):
        """Update item quantity"""
        if qty <= 0:
            self.delete()
            return None
        else:
            self.quantity = qty
            self.save()
            return self

    def calculate_subtotal(self):
        """Calculate item subtotal"""
        return self.unit_price * self.quantity
