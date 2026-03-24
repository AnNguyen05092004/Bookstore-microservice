from django.urls import path
from .views import (
    ReviewListCreate,
    ReviewDetail,
    MarkReviewHelpful,
    RatingListCreate,
    BookRatingSummary,
    HealthCheck,
)

urlpatterns = [
    # Review CRUD and helpful APIs
    path("reviews/", ReviewListCreate.as_view(), name="review-list-create"),
    path("reviews/<uuid:review_id>/", ReviewDetail.as_view(), name="review-detail"),
    path(
        "reviews/<uuid:review_id>/helpful/",
        MarkReviewHelpful.as_view(),
        name="mark-review-helpful",
    ),
    # Rating APIs
    path("ratings/", RatingListCreate.as_view(), name="rating-list-create"),
    path(
        "books/<uuid:book_id>/rating-summary/",
        BookRatingSummary.as_view(),
        name="book-rating-summary",
    ),
    # Service health endpoint
    path("health/", HealthCheck.as_view(), name="health-check"),
]
