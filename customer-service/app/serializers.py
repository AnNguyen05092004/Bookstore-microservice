"""
Customer Service - Serializers
"""

from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer cho Customer model"""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Customer
        fields = [
            "customer_id",
            "customer_code",
            "username",
            "email",
            "password_hash",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "date_of_birth",
            "gender",
            "avatar_url",
            "loyalty_points",
            "tier",
            "is_active",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "customer_id",
            "customer_code",
            "loyalty_points",
            "tier",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {"password_hash": {"write_only": True}}


class CustomerCreateSerializer(serializers.ModelSerializer):
    """Serializer cho tạo mới Customer"""

    class Meta:
        model = Customer
        fields = [
            "username",
            "email",
            "password_hash",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "gender",
        ]

    def create(self, validated_data):
        # Trong thực tế nên hash password
        customer = Customer.objects.create(**validated_data)
        return customer


class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer cho cập nhật Customer"""

    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "gender",
            "avatar_url",
        ]
