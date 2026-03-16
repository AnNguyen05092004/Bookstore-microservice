"""
Recommender AI Service - Models
Chuyển từ BookStore_Mono/bookstore/apps/recommendations/models.py
"""

import uuid
from django.db import models
from django.utils import timezone


class RecommendationEngine(models.Model):
    """AI Recommendation Engine model"""

    ALGORITHM_CHOICES = [
        ("collaborative", "Collaborative Filtering"),
        ("content_based", "Content-Based"),
        ("hybrid", "Hybrid"),
        ("popularity", "Popularity-Based"),
    ]

    model_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    algorithm_type = models.CharField(
        max_length=100, choices=ALGORITHM_CHOICES, default="hybrid"
    )
    version = models.CharField(max_length=50, blank=True, null=True)
    accuracy_score = models.DecimalField(
        max_digits=5, decimal_places=4, blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    parameters = models.JSONField(default=dict, blank=True)
    trained_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recommendation_engine"

    def __str__(self):
        return f"Model {self.model_id} ({self.algorithm_type})"

    def train_model(self):
        """Train the recommendation model"""
        self.trained_at = timezone.now()
        self.save()


class UserBehaviour(models.Model):
    """User Behaviour Tracking model"""

    ACTION_TYPE_CHOICES = [
        ("view", "View"),
        ("search", "Search"),
        ("click", "Click"),
        ("add_to_cart", "Add to Cart"),
        ("wishlist", "Add to Wishlist"),
        ("purchase", "Purchase"),
        ("share", "Share"),
    ]

    behaviour_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    customer_id = models.UUIDField()  # Reference to customer-service
    book_id = models.UUIDField(blank=True, null=True)  # Reference to book-service
    action_type = models.CharField(max_length=50, choices=ACTION_TYPE_CHOICES)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    search_query = models.CharField(max_length=500, blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_behaviour"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer_id} {self.action_type}"


class Recommendation(models.Model):
    """Book Recommendation result"""

    recommendation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    customer_id = models.UUIDField()
    book_id = models.UUIDField()
    score = models.FloatField(default=0)  # Recommendation score
    reason = models.CharField(max_length=255, blank=True, null=True)
    engine = models.ForeignKey(
        RecommendationEngine, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recommendation"
        ordering = ["-score"]
        unique_together = ("customer_id", "book_id")

    def __str__(self):
        return f"Recommend {self.book_id} for {self.customer_id}"
