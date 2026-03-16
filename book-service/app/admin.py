from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "book_id",
        "title",
        "price",
        "stock_quantity",
        "status",
        "average_rating",
        "created_at",
    ]
    list_filter = ["status", "is_featured", "is_bestseller", "language", "format"]
    search_fields = ["title", "isbn", "isbn13", "description"]
    readonly_fields = ["book_id", "created_at", "updated_at"]
