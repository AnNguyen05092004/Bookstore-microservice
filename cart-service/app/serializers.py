"""
Cart Service - Serializers
"""

from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer cho CartItem"""

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "cart_item_id",
            "cart",
            "book_id",
            "book_title",
            "quantity",
            "unit_price",
            "subtotal",
            "added_at",
        ]
        read_only_fields = ["cart_item_id", "subtotal", "added_at"]

    def get_subtotal(self, obj):
        return float(obj.calculate_subtotal())


class CartSerializer(serializers.ModelSerializer):
    """Serializer cho Cart"""

    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "cart_id",
            "customer_id",
            "session_id",
            "is_active",
            "items",
            "total",
            "item_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["cart_id", "created_at", "updated_at"]

    def get_total(self, obj):
        return float(obj.calculate_total())

    def get_item_count(self, obj):
        return obj.get_item_count()


class CartCreateSerializer(serializers.ModelSerializer):
    """Serializer cho tạo Cart"""

    class Meta:
        model = Cart
        fields = ["customer_id", "session_id"]


class AddCartItemSerializer(serializers.Serializer):
    """Serializer cho thêm item vào cart"""

    book_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer cho cập nhật quantity"""

    quantity = serializers.IntegerField(min_value=0)
