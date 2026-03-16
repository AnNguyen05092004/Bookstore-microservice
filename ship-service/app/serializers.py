"""Ship Service - Serializers"""

from rest_framework import serializers
from .models import Shipping


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = "__all__"
        read_only_fields = [
            "shipping_id",
            "tracking_code",
            "fee",
            "created_at",
            "updated_at",
        ]


class CreateShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = ["order_id", "shipping_method", "carrier", "shipping_address"]


class UpdateShippingStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Shipping.STATUS_CHOICES)


class TrackingSerializer(serializers.Serializer):
    tracking_code = serializers.CharField()
    status = serializers.CharField()
    carrier = serializers.CharField(allow_null=True)
    shipped_date = serializers.DateTimeField(allow_null=True)
    estimated_delivery = serializers.DateField(allow_null=True)
    actual_delivery = serializers.DateTimeField(allow_null=True)
