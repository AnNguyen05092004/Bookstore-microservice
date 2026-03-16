from django.contrib import admin
from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "customer_id",
        "status",
        "total_amount",
        "order_date",
    ]
    list_filter = ["status"]
    search_fields = ["order_number", "customer_id"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "book_title", "quantity", "unit_price", "total_price"]
