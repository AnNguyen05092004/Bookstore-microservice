"""
Book Service - Views
Theo mẫu từ PDF APPENDIX section 7.4.3
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Book
from .serializers import (
    BookSerializer,
    BookCreateSerializer,
    BookUpdateSerializer,
    BookStockSerializer,
)


class BookListCreate(APIView):
    """
    GET: Lấy danh sách sách (có filter, search)
    POST: Tạo sách mới (Staff only trong thực tế)
    """

    def get(self, request):
        books = Book.objects.all()

        # Filter by status
        book_status = request.query_params.get("status")
        if book_status:
            books = books.filter(status=book_status)

        # Filter by category
        category_id = request.query_params.get("category_id")
        if category_id:
            books = books.filter(category_id=category_id)

        # Filter by author
        author_id = request.query_params.get("author_id")
        if author_id:
            books = books.filter(author_id=author_id)

        # Search by title
        search = request.query_params.get("search")
        if search:
            books = books.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(isbn__icontains=search)
            )

        # Filter featured/bestseller
        if request.query_params.get("featured") == "true":
            books = books.filter(is_featured=True)
        if request.query_params.get("bestseller") == "true":
            books = books.filter(is_bestseller=True)

        # Ordering
        ordering = request.query_params.get("ordering", "-created_at")
        books = books.order_by(ordering)

        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookCreateSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()
            return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetail(APIView):
    """
    GET: Lấy thông tin 1 sách
    PUT: Cập nhật thông tin sách
    DELETE: Xóa sách
    """

    def get(self, request, book_id):
        book = get_object_or_404(Book, book_id=book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, book_id):
        book = get_object_or_404(Book, book_id=book_id)
        serializer = BookUpdateSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(BookSerializer(book).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, book_id):
        """Partial update"""
        return self.put(request, book_id)

    def delete(self, request, book_id):
        book = get_object_or_404(Book, book_id=book_id)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookStock(APIView):
    """
    GET: Kiểm tra stock của sách
    POST: Cập nhật stock (tăng/giảm)
    """

    def get(self, request, book_id):
        book = get_object_or_404(Book, book_id=book_id)
        return Response(
            {
                "book_id": str(book.book_id),
                "title": book.title,
                "stock_quantity": book.stock_quantity,
                "status": book.status,
            }
        )

    def post(self, request, book_id):
        book = get_object_or_404(Book, book_id=book_id)
        serializer = BookStockSerializer(data=request.data)

        if serializer.is_valid():
            quantity_change = serializer.validated_data["quantity_change"]
            new_stock = book.update_stock(quantity_change)
            return Response(
                {
                    "book_id": str(book.book_id),
                    "stock_quantity": new_stock,
                    "status": book.status,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookRating(APIView):
    """
    POST: Cập nhật rating từ comment-rate-service
    """

    def post(self, request, book_id):
        book = get_object_or_404(Book, book_id=book_id)

        new_avg = request.data.get("average_rating")
        review_count = request.data.get("total_reviews")

        if new_avg is not None and review_count is not None:
            book.update_rating(new_avg, review_count)
            return Response(
                {
                    "book_id": str(book.book_id),
                    "average_rating": float(book.average_rating),
                    "total_reviews": book.total_reviews,
                }
            )

        return Response(
            {"error": "average_rating and total_reviews required"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class HealthCheck(APIView):
    """Health check endpoint"""

    def get(self, request):
        return Response({"status": "healthy", "service": "book-service"})
