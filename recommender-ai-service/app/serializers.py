"""Recommender AI Service - Serializers"""

from rest_framework import serializers
from .models import RecommendationEngine, UserBehaviour, Recommendation


class RecommendationEngineSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationEngine
        fields = "__all__"


class UserBehaviourSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBehaviour
        fields = "__all__"
        read_only_fields = ["behaviour_id", "created_at"]


class TrackBehaviourSerializer(serializers.Serializer):
    customer_id = serializers.UUIDField()
    book_id = serializers.UUIDField(required=False)
    action_type = serializers.ChoiceField(choices=UserBehaviour.ACTION_TYPE_CHOICES)
    session_id = serializers.CharField(required=False, allow_blank=True)
    search_query = serializers.CharField(required=False, allow_blank=True)
    metadata = serializers.JSONField(required=False, default=dict)


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = "__all__"


class RecommendedBookSerializer(serializers.Serializer):
    book_id = serializers.UUIDField()
    score = serializers.FloatField()
    reason = serializers.CharField()
