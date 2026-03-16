"""Recommender AI Service - Views"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Count
import requests
import logging
import random

from .models import RecommendationEngine, UserBehaviour, Recommendation
from .serializers import (
    RecommendationEngineSerializer,
    UserBehaviourSerializer,
    TrackBehaviourSerializer,
    RecommendationSerializer,
)

logger = logging.getLogger(__name__)
BOOK_SERVICE_URL = getattr(settings, "BOOK_SERVICE_URL", "http://book-service:8000")


class TrackBehaviour(APIView):
    """POST: Track user behaviour"""

    def post(self, request):
        serializer = TrackBehaviourSerializer(data=request.data)
        if serializer.is_valid():
            behaviour = UserBehaviour.objects.create(**serializer.validated_data)
            return Response(
                UserBehaviourSerializer(behaviour).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetRecommendations(APIView):
    """GET: Get book recommendations for customer"""

    def get(self, request, customer_id):
        limit = int(request.query_params.get("limit", 10))

        # Get cached recommendations
        recommendations = Recommendation.objects.filter(
            customer_id=customer_id
        ).order_by("-score")[:limit]

        if recommendations.exists():
            result = [
                {"book_id": str(r.book_id), "score": r.score, "reason": r.reason}
                for r in recommendations
            ]
            return Response(result)

        # Generate new recommendations
        recommendations = self._generate_recommendations(customer_id, limit)
        return Response(recommendations)

    def _generate_recommendations(self, customer_id, limit):
        """Simple recommendation algorithm"""
        recommendations = []

        # Get user's viewed/purchased books
        viewed_books = (
            UserBehaviour.objects.filter(
                customer_id=customer_id,
                action_type__in=["view", "purchase", "add_to_cart"],
            )
            .values_list("book_id", flat=True)
            .distinct()
        )

        # Get popular books from book-service
        try:
            response = requests.get(
                f"{BOOK_SERVICE_URL}/books/",
                params={"ordering": "-total_sold", "status": "available"},
                timeout=5,
            )
            if response.status_code == 200:
                books = response.json()
                for book in books[:limit]:
                    book_id = book.get("book_id")
                    if book_id not in viewed_books:
                        score = random.uniform(0.5, 1.0)
                        reason = (
                            "Popular book"
                            if book.get("is_bestseller")
                            else "Recommended for you"
                        )

                        recommendations.append(
                            {
                                "book_id": book_id,
                                "score": round(score, 2),
                                "reason": reason,
                            }
                        )

                        # Cache recommendation
                        Recommendation.objects.update_or_create(
                            customer_id=customer_id,
                            book_id=book_id,
                            defaults={"score": score, "reason": reason},
                        )
        except Exception as e:
            logger.error(f"Error fetching books: {e}")

        return recommendations[:limit]


class PopularBooks(APIView):
    """GET: Get popular books based on user behaviour"""

    def get(self, request):
        limit = int(request.query_params.get("limit", 10))

        # Get most viewed/purchased books
        popular = (
            UserBehaviour.objects.filter(
                action_type__in=["view", "purchase"], book_id__isnull=False
            )
            .values("book_id")
            .annotate(count=Count("behaviour_id"))
            .order_by("-count")[:limit]
        )

        return Response(
            [
                {"book_id": str(item["book_id"]), "interactions": item["count"]}
                for item in popular
            ]
        )


class CustomerHistory(APIView):
    """GET: Get customer behaviour history"""

    def get(self, request, customer_id):
        behaviours = UserBehaviour.objects.filter(customer_id=customer_id)[:50]
        return Response(UserBehaviourSerializer(behaviours, many=True).data)


class EngineList(APIView):
    """GET/POST recommendation engines"""

    def get(self, request):
        engines = RecommendationEngine.objects.filter(is_active=True)
        return Response(RecommendationEngineSerializer(engines, many=True).data)

    def post(self, request):
        serializer = RecommendationEngineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthCheck(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "recommender-ai-service"})
