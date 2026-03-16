from django.contrib import admin
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["cart_id", "customer_id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["customer_id", "session_id"]
    readonly_fields = ["cart_id", "created_at", "updated_at"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        "cart_item_id",
        "cart",
        "book_id",
        "book_title",
        "quantity",
        "unit_price",
    ]
    search_fields = ["book_id", "book_title"]
    readonly_fields = ["cart_item_id", "added_at"]
