from django.contrib import admin
from .models import Shipping


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = [
        "shipping_id",
        "order_id",
        "shipping_method",
        "status",
        "tracking_code",
        "fee",
    ]
    list_filter = ["status", "shipping_method"]
    search_fields = ["order_id", "tracking_code"]
