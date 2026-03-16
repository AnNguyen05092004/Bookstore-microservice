"""
Book Service - Models
Chuyển từ BookStore_Mono/bookstore/apps/books/models.py (Book model)
"""

import uuid
from django.db import models


class Book(models.Model):
    """Book model - chứa thông tin sách"""

    STATUS_CHOICES = [
        ("available", "Available"),
        ("out_of_stock", "Out of Stock"),
        ("discontinued", "Discontinued"),
        ("coming_soon", "Coming Soon"),
    ]

    book_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Lưu ID reference đến catalog-service (author, publisher, category)
    author_id = models.UUIDField(blank=True, null=True)  # Reference to catalog-service
    publisher_id = models.UUIDField(
        blank=True, null=True
    )  # Reference to catalog-service
    category_id = models.UUIDField(
        blank=True, null=True
    )  # Reference to catalog-service

    title = models.CharField(max_length=500)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    isbn13 = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    short_description = models.CharField(max_length=500, blank=True, null=True)

    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    original_price = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    cost_price = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )

    # Inventory (simplified - full inventory in separate service)
    stock_quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=5)

    # Book details
    page_count = models.IntegerField(blank=True, null=True)
    weight_grams = models.IntegerField(blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=50, default="Vietnamese")
    format = models.CharField(max_length=50, default="Paperback")
    publish_year = models.IntegerField(blank=True, null=True)
    publish_date = models.DateField(blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True, null=True)

    # Status and flags
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default="available"
    )
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)

    # Ratings (synced from comment-rate-service)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    total_sold = models.IntegerField(default=0)

    # Cover image
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "book"
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def update_stock(self, quantity_change):
        """Update stock quantity"""
        self.stock_quantity += quantity_change
        if self.stock_quantity <= 0:
            self.status = "out_of_stock"
        elif self.status == "out_of_stock":
            self.status = "available"
        self.save()
        return self.stock_quantity

    def update_rating(self, new_avg, review_count):
        """Update rating from comment-rate-service"""
        self.average_rating = new_avg
        self.total_reviews = review_count
        self.save()

    def increment_sold(self, quantity=1):
        """Increment total sold count"""
        self.total_sold += quantity
        self.save()
