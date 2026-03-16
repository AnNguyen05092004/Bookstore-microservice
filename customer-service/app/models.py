"""
Customer Service - Models
Chuyển từ BookStore_Mono/bookstore/apps/accounts/models.py (Customer model)
"""

import uuid
from django.db import models


class Customer(models.Model):
    """Customer model - độc lập, không phụ thuộc User model"""

    TIER_CHOICES = [
        ("Bronze", "Bronze"),
        ("Silver", "Silver"),
        ("Gold", "Gold"),
        ("Platinum", "Platinum"),
    ]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password_hash = models.CharField(max_length=255)  # Trong thực tế nên hash
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=20, choices=GENDER_CHOICES, blank=True, null=True
    )
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)
    tier = models.CharField(max_length=50, choices=TIER_CHOICES, default="Bronze")
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customer"
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"Customer: {self.username}"

    @property
    def full_name(self):
        """Get customer full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def add_loyalty_points(self, points):
        """Add loyalty points and update tier"""
        self.loyalty_points += points
        self.update_tier()
        self.save()

    def update_tier(self):
        """Update customer tier based on points"""
        if self.loyalty_points >= 10000:
            self.tier = "Platinum"
        elif self.loyalty_points >= 5000:
            self.tier = "Gold"
        elif self.loyalty_points >= 1000:
            self.tier = "Silver"
        else:
            self.tier = "Bronze"

    def save(self, *args, **kwargs):
        """Generate customer_code if not exists"""
        if not self.customer_code:
            import hashlib
            import time

            unique_str = f"{time.time()}{uuid.uuid4()}"
            self.customer_code = (
                "CUS-" + hashlib.md5(unique_str.encode()).hexdigest()[:8].upper()
            )
        super().save(*args, **kwargs)
