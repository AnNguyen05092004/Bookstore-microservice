"""Comment Rate Service - Serializers"""

from rest_framework import serializers
from .models import Review, Rating


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["review_id", "created_at", "updated_at", "helpful_count"]


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "book_id",
            "customer_id",
            "order_item_id",
            "title",
            "content",
            "is_verified_purchase",
        ]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"
        read_only_fields = ["rating_id", "created_at", "updated_at"]


class CreateRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["book_id", "customer_id", "score"]


class BookRatingSummarySerializer(serializers.Serializer):
    book_id = serializers.UUIDField()
    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    total_ratings = serializers.IntegerField()
