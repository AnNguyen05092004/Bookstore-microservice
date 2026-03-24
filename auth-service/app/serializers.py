"""Staff Service - Serializers"""

from rest_framework import serializers
from .models import Staff, StaffSession


class StaffSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Staff
        fields = [
            "staff_id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "role",
            "department",
            "employee_id",
            "is_active",
            "hire_date",
            "created_at",
            "updated_at",
            "last_login",
        ]
        read_only_fields = ["staff_id", "created_at", "updated_at", "last_login"]


class StaffCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Staff
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "role",
            "department",
            "employee_id",
            "hire_date",
        ]

    def create(self, validated_data):
        import hashlib

        password = validated_data.pop("password")
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        validated_data["password_hash"] = password_hash
        return Staff.objects.create(**validated_data)


class StaffLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class StaffSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffSession
        fields = "__all__"
