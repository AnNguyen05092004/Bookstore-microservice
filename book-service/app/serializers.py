"""
Book Service - Serializers
"""

from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer cho Book model"""

    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["book_id", "created_at", "updated_at"]


class BookCreateSerializer(serializers.ModelSerializer):
    """Serializer cho tạo mới Book"""

    class Meta:
        model = Book
        fields = [
            "title",
            "isbn",
            "isbn13",
            "description",
            "short_description",
            "price",
            "original_price",
            "cost_price",
            "stock_quantity",
            "page_count",
            "weight_grams",
            "dimensions",
            "language",
            "format",
            "publish_year",
            "publish_date",
            "edition",
            "status",
            "is_featured",
            "is_bestseller",
            "cover_image_url",
            "author_id",
            "publisher_id",
            "category_id",
        ]


class BookUpdateSerializer(serializers.ModelSerializer):
    """Serializer cho cập nhật Book"""

    class Meta:
        model = Book
        fields = [
            "title",
            "description",
            "short_description",
            "price",
            "original_price",
            "stock_quantity",
            "status",
            "is_featured",
            "is_bestseller",
            "cover_image_url",
            "author_id",
            "publisher_id",
            "category_id",
        ]


class BookStockSerializer(serializers.Serializer):
    """Serializer cho cập nhật stock"""

    quantity_change = serializers.IntegerField()
