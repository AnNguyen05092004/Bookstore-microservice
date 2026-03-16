from django.contrib import admin
from .models import Publisher, Author, Category, Tag, BookLanguage, BookFormat


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ["publisher_id", "name", "email", "is_active"]
    search_fields = ["name"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["author_id", "name", "nationality", "is_active"]
    search_fields = ["name"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "category_id",
        "name",
        "slug",
        "parent",
        "display_order",
        "is_active",
    ]
    list_filter = ["is_active", "parent"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["tag_id", "name", "slug", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BookLanguage)
class BookLanguageAdmin(admin.ModelAdmin):
    list_display = ["language_id", "code", "name", "is_active"]


@admin.register(BookFormat)
class BookFormatAdmin(admin.ModelAdmin):
    list_display = ["format_id", "name", "is_active"]
