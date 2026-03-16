"""
Book Service - URLs
"""

from django.urls import path
from .views import BookListCreate, BookDetail, BookStock, BookRating, HealthCheck

urlpatterns = [
    path("books/", BookListCreate.as_view(), name="book-list-create"),
    path("books/<uuid:book_id>/", BookDetail.as_view(), name="book-detail"),
    path("books/<uuid:book_id>/stock/", BookStock.as_view(), name="book-stock"),
    path("books/<uuid:book_id>/rating/", BookRating.as_view(), name="book-rating"),
    path("health/", HealthCheck.as_view(), name="health-check"),
]
