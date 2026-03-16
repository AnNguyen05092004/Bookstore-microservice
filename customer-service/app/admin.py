from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "customer_id",
        "customer_code",
        "username",
        "email",
        "tier",
        "is_active",
        "created_at",
    ]
    list_filter = ["tier", "is_active", "is_verified", "gender"]
    search_fields = ["username", "email", "customer_code", "first_name", "last_name"]
    readonly_fields = ["customer_id", "customer_code", "created_at", "updated_at"]
