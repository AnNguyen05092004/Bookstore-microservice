from django.urls import path
from .views import (
    PublisherList,
    PublisherDetail,
    AuthorList,
    AuthorDetail,
    CategoryList,
    CategoryDetail,
    TagList,
    TagDetail,
    LanguageList,
    FormatList,
    HealthCheck,
)

urlpatterns = [
    # Publisher APIs
    path("publishers/", PublisherList.as_view(), name="publisher-list"),
    path(
        "publishers/<uuid:publisher_id>/",
        PublisherDetail.as_view(),
        name="publisher-detail",
    ),
    # Author APIs
    path("authors/", AuthorList.as_view(), name="author-list"),
    path("authors/<uuid:author_id>/", AuthorDetail.as_view(), name="author-detail"),
    # Category APIs
    path("categories/", CategoryList.as_view(), name="category-list"),
    path(
        "categories/<uuid:category_id>/",
        CategoryDetail.as_view(),
        name="category-detail",
    ),
    # Tag APIs
    path("tags/", TagList.as_view(), name="tag-list"),
    path("tags/<uuid:tag_id>/", TagDetail.as_view(), name="tag-detail"),
    # Metadata lookup APIs
    path("languages/", LanguageList.as_view(), name="language-list"),
    path("formats/", FormatList.as_view(), name="format-list"),
    # Service health endpoint
    path("health/", HealthCheck.as_view(), name="health-check"),
]
