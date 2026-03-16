"""
Comment Rate Service - Models
Chuyển từ BookStore_Mono/bookstore/apps/reviews/models.py
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """Book Review model"""

    review_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_id = models.UUIDField()  # Reference to book-service
    customer_id = models.UUIDField()  # Reference to customer-service
    order_item_id = models.UUIDField(
        blank=True, null=True
    )  # Reference to order-service
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "review"
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review {self.review_id} for Book {self.book_id}"

    def mark_helpful(self):
        """Increment helpful count"""
        self.helpful_count += 1
        self.save()


class Rating(models.Model):
    """Book Rating model"""

    rating_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_id = models.UUIDField()  # Reference to book-service
    customer_id = models.UUIDField()  # Reference to customer-service
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rating"
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
        unique_together = ("book_id", "customer_id")

    def __str__(self):
        return f"Rating {self.score}/5 for Book {self.book_id}"
