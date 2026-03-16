from django.contrib import admin
from .models import Review, Rating


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "review_id",
        "book_id",
        "customer_id",
        "is_approved",
        "helpful_count",
        "created_at",
    ]
    list_filter = ["is_approved", "is_verified_purchase"]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["rating_id", "book_id", "customer_id", "score", "created_at"]
    list_filter = ["score"]
