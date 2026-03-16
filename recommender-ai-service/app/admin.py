from django.contrib import admin
from .models import RecommendationEngine, UserBehaviour, Recommendation


@admin.register(RecommendationEngine)
class RecommendationEngineAdmin(admin.ModelAdmin):
    list_display = ["model_id", "algorithm_type", "version", "is_active", "trained_at"]


@admin.register(UserBehaviour)
class UserBehaviourAdmin(admin.ModelAdmin):
    list_display = [
        "behaviour_id",
        "customer_id",
        "book_id",
        "action_type",
        "created_at",
    ]
    list_filter = ["action_type"]


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ["recommendation_id", "customer_id", "book_id", "score", "reason"]
