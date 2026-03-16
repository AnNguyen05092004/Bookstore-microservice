"""Order Service - Serializers"""

from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"
        read_only_fields = ["order_item_id", "total_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ["order_id", "order_number", "created_at", "updated_at"]


class CreateOrderSerializer(serializers.Serializer):
    """Serializer cho tạo order từ cart"""

    customer_id = serializers.UUIDField()
    shipping_address = serializers.CharField(required=False, allow_blank=True)
    billing_address = serializers.CharField(required=False, allow_blank=True)
    shipping_method = serializers.CharField(default="standard")
    payment_method = serializers.CharField(default="cod")
    notes = serializers.CharField(required=False, allow_blank=True)


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
