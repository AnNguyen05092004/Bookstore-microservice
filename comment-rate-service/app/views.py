"""Comment Rate Service - Views"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from django.conf import settings
import requests
import logging

from .models import Review, Rating
from .serializers import (
    ReviewSerializer,
    CreateReviewSerializer,
    RatingSerializer,
    CreateRatingSerializer,
)

logger = logging.getLogger(__name__)
BOOK_SERVICE_URL = getattr(settings, "BOOK_SERVICE_URL", "http://book-service:8000")


class ReviewListCreate(APIView):
    """GET/POST reviews"""

    def get(self, request):
        book_id = request.query_params.get("book_id")
        customer_id = request.query_params.get("customer_id")

        reviews = Review.objects.filter(is_approved=True)
        if book_id:
            reviews = reviews.filter(book_id=book_id)
        if customer_id:
            reviews = reviews.filter(customer_id=customer_id)

        return Response(ReviewSerializer(reviews, many=True).data)

    def post(self, request):
        serializer = CreateReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save()

            # Also create/update rating if score is provided
            score = request.data.get("score")
            if score:
                try:
                    score = int(score)
                    if 1 <= score <= 5:
                        Rating.objects.update_or_create(
                            book_id=review.book_id,
                            customer_id=review.customer_id,
                            defaults={"score": score},
                        )
                except (TypeError, ValueError):
                    pass

            # Update book rating in book-service
            self._update_book_rating(review.book_id)
            return Response(
                ReviewSerializer(review).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _update_book_rating(self, book_id):
        """Sync rating to book-service"""
        try:
            stats = Rating.objects.filter(book_id=book_id).aggregate(
                avg=Avg("score"), count=Count("rating_id")
            )
            review_count = Review.objects.filter(
                book_id=book_id, is_approved=True
            ).count()

            requests.post(
                f"{BOOK_SERVICE_URL}/books/{book_id}/rating/",
                json={
                    "average_rating": stats["avg"] or 0,
                    "total_reviews": review_count,
                },
                timeout=5,
            )
        except Exception as e:
            logger.error(f"Error updating book rating: {e}")


class ReviewDetail(APIView):
    """GET/PUT/DELETE single review"""

    def get(self, request, review_id):
        review = get_object_or_404(Review, review_id=review_id)
        return Response(ReviewSerializer(review).data)

    def put(self, request, review_id):
        review = get_object_or_404(Review, review_id=review_id)
        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, review_id):
        review = get_object_or_404(Review, review_id=review_id)
        book_id = review.book_id
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkReviewHelpful(APIView):
    """POST: Mark review as helpful"""

    def post(self, request, review_id):
        review = get_object_or_404(Review, review_id=review_id)
        review.mark_helpful()
        return Response(ReviewSerializer(review).data)


class RatingListCreate(APIView):
    """GET/POST ratings"""

    def get(self, request):
        book_id = request.query_params.get("book_id")
        if book_id:
            ratings = Rating.objects.filter(book_id=book_id)
        else:
            ratings = Rating.objects.all()
        return Response(RatingSerializer(ratings, many=True).data)

    def post(self, request):
        book_id = request.data.get("book_id")
        customer_id = request.data.get("customer_id")
        score = request.data.get("score")

        if not all([book_id, customer_id, score]):
            return Response(
                {"error": "book_id, customer_id, and score are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            score = int(score)
            if not (1 <= score <= 5):
                return Response(
                    {"error": "score must be between 1 and 5"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (TypeError, ValueError):
            return Response(
                {"error": "score must be a number"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Update or create rating
        rating, created = Rating.objects.update_or_create(
            book_id=book_id,
            customer_id=customer_id,
            defaults={"score": score},
        )

        # Update book rating in book-service
        self._update_book_rating(rating.book_id)

        return Response(
            RatingSerializer(rating).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def _update_book_rating(self, book_id):
        """Sync rating to book-service"""
        try:
            stats = Rating.objects.filter(book_id=book_id).aggregate(
                avg=Avg("score"), count=Count("rating_id")
            )
            review_count = Review.objects.filter(
                book_id=book_id, is_approved=True
            ).count()

            requests.post(
                f"{BOOK_SERVICE_URL}/books/{book_id}/rating/",
                json={
                    "average_rating": stats["avg"] or 0,
                    "total_reviews": review_count,
                },
                timeout=5,
            )
        except Exception as e:
            logger.error(f"Error updating book rating: {e}")


class BookRatingSummary(APIView):
    """GET: Get rating summary for a book"""

    def get(self, request, book_id):
        stats = Rating.objects.filter(book_id=book_id).aggregate(
            avg=Avg("score"), count=Count("rating_id")
        )
        review_count = Review.objects.filter(book_id=book_id, is_approved=True).count()

        return Response(
            {
                "book_id": str(book_id),
                "average_rating": round(stats["avg"] or 0, 2),
                "total_ratings": stats["count"],
                "total_reviews": review_count,
            }
        )


class HealthCheck(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "comment-rate-service"})
