"""
Book Service - URLs
"""

from django.urls import path
from .views import (
    BookListCreate,
    BookDetail,
    BookStock,
    BookRating,
    BookSales,
    HealthCheck,
)

urlpatterns = [
    # Book catalog CRUD APIs
    path("books/", BookListCreate.as_view(), name="book-list-create"),
    path("books/<uuid:book_id>/", BookDetail.as_view(), name="book-detail"),
    # Inventory/rating/sales sync APIs
    path("books/<uuid:book_id>/stock/", BookStock.as_view(), name="book-stock"),
    path("books/<uuid:book_id>/rating/", BookRating.as_view(), name="book-rating"),
    path("books/<uuid:book_id>/sales/", BookSales.as_view(), name="book-sales"),
    # Service health endpoint
    path("health/", HealthCheck.as_view(), name="health-check"),
]
