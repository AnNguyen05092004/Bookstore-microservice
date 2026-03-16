"""Catalog Service - Views"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Publisher, Author, Category, Tag, BookLanguage, BookFormat
from .serializers import (
    PublisherSerializer,
    AuthorSerializer,
    CategorySerializer,
    TagSerializer,
    BookLanguageSerializer,
    BookFormatSerializer,
)


# Publisher Views
class PublisherList(APIView):
    def get(self, request):
        publishers = Publisher.objects.filter(is_active=True)
        return Response(PublisherSerializer(publishers, many=True).data)

    def post(self, request):
        serializer = PublisherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublisherDetail(APIView):
    def get(self, request, publisher_id):
        publisher = get_object_or_404(Publisher, publisher_id=publisher_id)
        return Response(PublisherSerializer(publisher).data)

    def put(self, request, publisher_id):
        publisher = get_object_or_404(Publisher, publisher_id=publisher_id)
        serializer = PublisherSerializer(publisher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, publisher_id):
        publisher = get_object_or_404(Publisher, publisher_id=publisher_id)
        publisher.is_active = False
        publisher.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Author Views
class AuthorList(APIView):
    def get(self, request):
        authors = Author.objects.filter(is_active=True)
        search = request.query_params.get("search")
        if search:
            authors = authors.filter(name__icontains=search)
        return Response(AuthorSerializer(authors, many=True).data)

    def post(self, request):
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorDetail(APIView):
    def get(self, request, author_id):
        author = get_object_or_404(Author, author_id=author_id)
        return Response(AuthorSerializer(author).data)

    def put(self, request, author_id):
        author = get_object_or_404(Author, author_id=author_id)
        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, author_id):
        author = get_object_or_404(Author, author_id=author_id)
        author.is_active = False
        author.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Category Views
class CategoryList(APIView):
    def get(self, request):
        # Get only root categories (no parent)
        root_only = request.query_params.get("root", "false").lower() == "true"
        categories = Category.objects.filter(is_active=True)

        if root_only:
            categories = categories.filter(parent__isnull=True)

        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    def get(self, request, category_id):
        category = get_object_or_404(Category, category_id=category_id)
        return Response(CategorySerializer(category).data)

    def put(self, request, category_id):
        category = get_object_or_404(Category, category_id=category_id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, category_id):
        category = get_object_or_404(Category, category_id=category_id)
        category.is_active = False
        category.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Tag Views
class TagList(APIView):
    def get(self, request):
        tags = Tag.objects.filter(is_active=True)
        return Response(TagSerializer(tags, many=True).data)

    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagDetail(APIView):
    def get(self, request, tag_id):
        tag = get_object_or_404(Tag, tag_id=tag_id)
        return Response(TagSerializer(tag).data)

    def put(self, request, tag_id):
        tag = get_object_or_404(Tag, tag_id=tag_id)
        serializer = TagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, tag_id):
        tag = get_object_or_404(Tag, tag_id=tag_id)
        tag.is_active = False
        tag.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Language Views
class LanguageList(APIView):
    def get(self, request):
        languages = BookLanguage.objects.filter(is_active=True)
        return Response(BookLanguageSerializer(languages, many=True).data)

    def post(self, request):
        serializer = BookLanguageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Format Views
class FormatList(APIView):
    def get(self, request):
        formats = BookFormat.objects.filter(is_active=True)
        return Response(BookFormatSerializer(formats, many=True).data)

    def post(self, request):
        serializer = BookFormatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthCheck(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "catalog-service"})
