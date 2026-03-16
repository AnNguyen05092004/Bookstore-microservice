"""API Gateway - Views (routing to microservices & web UI)"""

import requests
import logging
from django.shortcuts import render
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def get_service_url(service_name):
    """Get service URL from settings"""
    urls = {
        "customer": settings.CUSTOMER_SERVICE_URL,
        "staff": settings.STAFF_SERVICE_URL,
        "catalog": settings.CATALOG_SERVICE_URL,
        "book": settings.BOOK_SERVICE_URL,
        "cart": settings.CART_SERVICE_URL,
        "order": settings.ORDER_SERVICE_URL,
        "pay": settings.PAY_SERVICE_URL,
        "ship": settings.SHIP_SERVICE_URL,
        "comment": settings.COMMENT_RATE_SERVICE_URL,
        "recommender": settings.RECOMMENDER_SERVICE_URL,
    }
    return urls.get(service_name)


def proxy_request(service_url, path, method="GET", data=None, params=None):
    """Generic proxy function to forward request to microservices"""
    url = f"{service_url}/{path}"
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return None, 400

        return response.json() if response.content else None, response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Service request failed: {e}")
        return {"error": str(e)}, 503


# ============ Web UI Views ============


def home(request):
    """Home page"""
    return render(request, "home.html")


def books_page(request):
    """Books listing page"""
    try:
        response = requests.get(f"{settings.BOOK_SERVICE_URL}/books/", timeout=10)
        books = response.json() if response.status_code == 200 else []
    except:
        books = []

    return render(request, "books.html", {"books": books})


def category_page(request, slug):
    """Category page - show books and authors for a category"""
    category_id = request.GET.get("id")
    category = None
    books = []
    authors = []
    author_map = {}

    # Fetch category info
    try:
        resp = requests.get(f"{settings.CATALOG_SERVICE_URL}/categories/", timeout=10)
        if resp.status_code == 200:
            for cat in resp.json():
                if cat.get("slug") == slug:
                    category = cat
                    if not category_id:
                        category_id = cat.get("category_id")
                    break
    except:
        pass

    if not category:
        category = {
            "name": slug.replace("-", " ").title(),
            "slug": slug,
            "description": "",
        }

    # Fetch books by category
    if category_id:
        try:
            resp = requests.get(
                f"{settings.BOOK_SERVICE_URL}/books/",
                params={"category_id": category_id},
                timeout=10,
            )
            if resp.status_code == 200:
                books = resp.json()
        except:
            pass

    # Fetch all authors to get names + filter those in this category
    try:
        resp = requests.get(f"{settings.CATALOG_SERVICE_URL}/authors/", timeout=10)
        if resp.status_code == 200:
            for a in resp.json():
                author_map[str(a.get("author_id"))] = a
    except:
        pass

    # Find unique authors from books in this category
    seen_author_ids = set()
    for book in books:
        aid = str(book.get("author_id", ""))
        if aid and aid != "None" and aid not in seen_author_ids:
            seen_author_ids.add(aid)
            author_info = author_map.get(aid)
            if author_info:
                authors.append(author_info)

    return render(
        request,
        "category.html",
        {
            "category": category,
            "books": books,
            "authors": authors,
            "author_map": author_map,
        },
    )


def book_detail_page(request, book_id):
    """Book detail page"""
    book = None
    reviews = []
    rating_map = {}
    customer_map = {}

    try:
        response = requests.get(
            f"{settings.BOOK_SERVICE_URL}/books/{book_id}/", timeout=10
        )
        if response.status_code == 200:
            book = response.json()
    except:
        pass

    try:
        # Fetch reviews
        response = requests.get(
            f"{settings.COMMENT_RATE_SERVICE_URL}/reviews/",
            params={"book_id": str(book_id)},
            timeout=10,
        )
        if response.status_code == 200:
            reviews = response.json()

        # Fetch ratings for this book
        rating_resp = requests.get(
            f"{settings.COMMENT_RATE_SERVICE_URL}/ratings/",
            params={"book_id": str(book_id)},
            timeout=10,
        )
        if rating_resp.status_code == 200:
            rating_map = {str(r["customer_id"]): r["score"] for r in rating_resp.json()}

        # Fetch customers to get names
        cust_resp = requests.get(
            f"{settings.CUSTOMER_SERVICE_URL}/customers/",
            timeout=10,
        )
        if cust_resp.status_code == 200:
            customer_map = {
                str(
                    c["customer_id"]
                ): f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
                or c.get("username")
                for c in cust_resp.json()
            }

        # Enrich reviews
        for review in reviews:
            c_id = str(review.get("customer_id", ""))
            review["rating"] = rating_map.get(c_id, 0)
            name = customer_map.get(c_id) or "Ẩn danh"
            review["customer_name"] = name
            review["customer_initial"] = name[0].upper() if name else "A"

    except Exception as e:
        logger.error(f"Error fetching review details: {e}")

    return render(request, "book_detail.html", {"book": book, "reviews": reviews})


def cart_page(request):
    """Shopping cart page"""
    customer_id = request.session.get("customer_id")
    cart = None

    if customer_id:
        try:
            response = requests.get(
                f"{settings.CART_SERVICE_URL}/carts/customer/{customer_id}/", timeout=10
            )
            if response.status_code == 200:
                cart = response.json()
        except:
            pass

    return render(request, "cart.html", {"cart": cart})


def login_page(request):
    """Login page"""
    return render(request, "login.html")


def register_page(request):
    """Register page"""
    return render(request, "register.html")


def checkout_page(request):
    """Checkout page"""
    return render(request, "checkout.html")


def orders_page(request):
    """Customer orders page"""
    return render(request, "orders.html")


# ============ Staff Web UI Views ============


def staff_login_page(request):
    """Staff login page"""
    return render(request, "staff_login.html")


def staff_dashboard_page(request):
    """Staff dashboard page"""
    return render(request, "staff_dashboard.html")


def staff_books_page(request):
    """Staff books management page"""
    return render(request, "staff_books.html")


def staff_customers_page(request):
    """Staff customers management page"""
    return render(request, "staff_customers.html")


def staff_orders_page(request):
    """Staff orders management page"""
    return render(request, "staff_orders.html")


def staff_catalog_page(request):
    """Staff catalog management page"""
    return render(request, "staff_catalog.html")


# ============ API Proxy Views ============


class BooksAPI(APIView):
    """Proxy books API"""

    def get(self, request):
        data, status_code = proxy_request(
            settings.BOOK_SERVICE_URL, "books/", params=request.query_params
        )
        return Response(data, status=status_code)

    def post(self, request):
        data, status_code = proxy_request(
            settings.BOOK_SERVICE_URL, "books/", method="POST", data=request.data
        )
        return Response(data, status=status_code)


class BookDetailAPI(APIView):
    """Proxy single book API"""

    def get(self, request, book_id):
        data, status_code = proxy_request(
            settings.BOOK_SERVICE_URL, f"books/{book_id}/"
        )
        return Response(data, status=status_code)

    def put(self, request, book_id):
        data, status_code = proxy_request(
            settings.BOOK_SERVICE_URL,
            f"books/{book_id}/",
            method="PUT",
            data=request.data,
        )
        return Response(data, status=status_code)

    def delete(self, request, book_id):
        data, status_code = proxy_request(
            settings.BOOK_SERVICE_URL, f"books/{book_id}/", method="DELETE"
        )
        return Response(data, status=status_code)


class CartAPI(APIView):
    """Proxy cart API"""

    def get(self, request, customer_id):
        data, status_code = proxy_request(
            settings.CART_SERVICE_URL, f"carts/{customer_id}/"
        )
        return Response(data, status=status_code)

    def post(self, request, customer_id):
        data, status_code = proxy_request(
            settings.CART_SERVICE_URL,
            f"carts/{customer_id}/items/",
            method="POST",
            data=request.data,
        )
        return Response(data, status=status_code)


class CartItemAPI(APIView):
    """Proxy cart item API"""

    def delete(self, request, customer_id, book_id):
        data, status_code = proxy_request(
            settings.CART_SERVICE_URL,
            f"carts/{customer_id}/items/{book_id}/",
            method="DELETE",
        )
        return Response(data, status=status_code)


class OrderAPI(APIView):
    """Proxy order API"""

    def get(self, request, customer_id=None):
        if customer_id:
            # Get orders by customer_id using query parameter
            data, status_code = proxy_request(
                settings.ORDER_SERVICE_URL,
                "orders/",
                params={"customer_id": str(customer_id)},
            )
        else:
            data, status_code = proxy_request(settings.ORDER_SERVICE_URL, "orders/")
        return Response(data, status=status_code)

    def post(self, request):
        data, status_code = proxy_request(
            settings.ORDER_SERVICE_URL, "orders/", method="POST", data=request.data
        )
        return Response(data, status=status_code)


class OrderDetailAPI(APIView):
    """Proxy order detail API - GET/PUT single order"""

    def get(self, request, order_id):
        data, status_code = proxy_request(
            settings.ORDER_SERVICE_URL, f"orders/{order_id}/"
        )
        return Response(data, status=status_code)

    def put(self, request, order_id):
        data, status_code = proxy_request(
            settings.ORDER_SERVICE_URL,
            f"orders/{order_id}/",
            method="PUT",
            data=request.data,
        )
        return Response(data, status=status_code)


class CancelOrderAPI(APIView):
    """Proxy cancel order API"""

    def post(self, request, order_id):
        data, status_code = proxy_request(
            settings.ORDER_SERVICE_URL, f"orders/{order_id}/cancel/", method="POST"
        )
        return Response(data, status=status_code)


class CustomerLoginAPI(APIView):
    """Proxy customer login"""

    def post(self, request):
        data, status_code = proxy_request(
            settings.CUSTOMER_SERVICE_URL, "login/", method="POST", data=request.data
        )
        if status_code == 200 and data.get("customer"):
            request.session["customer_id"] = data["customer"].get("customer_id")
        return Response(data, status=status_code)


class StaffLoginAPI(APIView):
    """Proxy staff login"""

    def post(self, request):
        data, status_code = proxy_request(
            settings.STAFF_SERVICE_URL, "login/", method="POST", data=request.data
        )
        if status_code == 200 and data.get("staff"):
            request.session["staff_id"] = data["staff"].get("staff_id")
        return Response(data, status=status_code)


class CustomerRegisterAPI(APIView):
    """Proxy customer registration"""

    def post(self, request):
        data, status_code = proxy_request(
            settings.CUSTOMER_SERVICE_URL,
            "customers/",
            method="POST",
            data=request.data,
        )
        return Response(data, status=status_code)


class RecommendationsAPI(APIView):
    """Proxy recommendations"""

    def get(self, request, customer_id):
        data, status_code = proxy_request(
            settings.RECOMMENDER_SERVICE_URL, f"recommendations/{customer_id}/"
        )
        return Response(data, status=status_code)


class CustomersAPI(APIView):
    """Proxy customers API"""

    def get(self, request):
        data, status_code = proxy_request(settings.CUSTOMER_SERVICE_URL, "customers/")
        return Response(data, status=status_code)


class CategoriesAPI(APIView):
    """Proxy categories API"""

    def get(self, request):
        data, status_code = proxy_request(settings.CATALOG_SERVICE_URL, "categories/")
        return Response(data, status=status_code)


class AuthorsAPI(APIView):
    """Proxy authors API"""

    def get(self, request):
        data, status_code = proxy_request(settings.CATALOG_SERVICE_URL, "authors/")
        return Response(data, status=status_code)


class PublishersAPI(APIView):
    """Proxy publishers API"""

    def get(self, request):
        data, status_code = proxy_request(settings.CATALOG_SERVICE_URL, "publishers/")
        return Response(data, status=status_code)


class TagsAPI(APIView):
    """Proxy tags API"""

    def get(self, request):
        data, status_code = proxy_request(settings.CATALOG_SERVICE_URL, "tags/")
        return Response(data, status=status_code)


class ReviewsAPI(APIView):
    """Proxy reviews API for book ratings"""

    def get(self, request):
        book_id = request.query_params.get("book_id")
        if book_id:
            data, status_code = proxy_request(
                settings.COMMENT_RATE_SERVICE_URL, f"reviews/book/{book_id}/"
            )
        else:
            data, status_code = proxy_request(
                settings.COMMENT_RATE_SERVICE_URL, "reviews/"
            )
        return Response(data, status=status_code)

    def post(self, request):
        data, status_code = proxy_request(
            settings.COMMENT_RATE_SERVICE_URL,
            "reviews/",
            method="POST",
            data=request.data,
        )
        return Response(data, status=status_code)


class RatingsAPI(APIView):
    """Proxy ratings API"""

    def post(self, request):
        data, status_code = proxy_request(
            settings.COMMENT_RATE_SERVICE_URL,
            "ratings/",
            method="POST",
            data=request.data,
        )
        return Response(data, status=status_code)


class HealthCheck(APIView):
    """Health check endpoint"""

    def get(self, request):
        services_health = {}
        services = [
            ("customer", settings.CUSTOMER_SERVICE_URL),
            ("staff", settings.STAFF_SERVICE_URL),
            ("catalog", settings.CATALOG_SERVICE_URL),
            ("book", settings.BOOK_SERVICE_URL),
            ("cart", settings.CART_SERVICE_URL),
            ("order", settings.ORDER_SERVICE_URL),
            ("pay", settings.PAY_SERVICE_URL),
            ("ship", settings.SHIP_SERVICE_URL),
            ("comment", settings.COMMENT_RATE_SERVICE_URL),
            ("recommender", settings.RECOMMENDER_SERVICE_URL),
        ]

        for name, url in services:
            try:
                response = requests.get(f"{url}/health/", timeout=3)
                services_health[name] = (
                    "healthy" if response.status_code == 200 else "unhealthy"
                )
            except:
                services_health[name] = "unavailable"

        return Response(
            {"status": "healthy", "service": "api-gateway", "services": services_health}
        )
