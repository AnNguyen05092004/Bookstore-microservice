"""Catalog Service - Serializers"""

from rest_framework import serializers
from .models import Publisher, Author, Category, Tag, BookLanguage, BookFormat


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = "__all__"
        read_only_fields = ["publisher_id", "created_at"]


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"
        read_only_fields = ["author_id", "created_at"]


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["category_id", "created_at"]

    def get_children(self, obj):
        if hasattr(obj, "children"):
            children = obj.children.filter(is_active=True)
            return CategorySerializer(children, many=True).data
        return []


class CategorySimpleSerializer(serializers.ModelSerializer):
    """Serializer đơn giản không có children để tránh infinite recursion"""

    class Meta:
        model = Category
        fields = ["category_id", "name", "slug", "description", "image"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ["tag_id", "created_at"]


class BookLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookLanguage
        fields = "__all__"
        read_only_fields = ["language_id"]


class BookFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookFormat
        fields = "__all__"
        read_only_fields = ["format_id"]
