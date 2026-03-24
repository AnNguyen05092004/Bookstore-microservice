"""API Gateway - Views (routing to microservices & web UI)"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps

import requests
from django.shortcuts import redirect, render
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
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return None, 400

        return response.json() if response.content else None, response.status_code
    except requests.exceptions.RequestException as e:
        logger.error(f"Service request failed: {e}")
        return {"error": str(e)}, 503


def _clear_auth_session(request):
    for key in ["jwt_token", "customer_id", "staff_id", "staff_role", "staff_name"]:
        if key in request.session:
            del request.session[key]


def _extract_bearer_token(request):
    raw = request.META.get("HTTP_AUTHORIZATION", "")
    if not raw:
        return ""
    parts = raw.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return ""


def _verify_token_remote(token, required_roles=None):
    payload = {"token": token}
    if required_roles:
        payload["required_roles"] = required_roles
    data, status_code = proxy_request(
        settings.AUTH_SERVICE_URL,
        "auth/verify/",
        method="POST",
        data=payload,
    )
    if status_code == 200 and data and data.get("valid"):
        return data.get("claims") or {}
    return {}


def _auth_claims(request):
    bearer = _extract_bearer_token(request)
    token = bearer or request.session.get("jwt_token") or ""
    if not token:
        return {}
    claims = _verify_token_remote(token)
    if not claims:
        if not bearer:
            _clear_auth_session(request)
        return {}
    if not bearer:
        request.session["jwt_token"] = token
        request.session["staff_role"] = claims.get("role") or ""
    return claims


def _staff_session_role(request):
    claims = _auth_claims(request)
    if claims.get("user_type") != "staff":
        return ""
    return (claims.get("role") or "").lower()


def _is_manager_role(role):
    return role in {"manager", "admin"}


def _role_required(allowed_roles, login_path):
    allowed = {r.lower() for r in allowed_roles}

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            claims = _auth_claims(request)
            role = (claims.get("role") or "").lower()
            if claims.get("user_type") != "staff" or not claims.get("sub") or not role:
                return redirect(login_path)
            if role not in allowed:
                if _is_manager_role(role):
                    return redirect("/manager/dashboard/")
                return redirect("/staff/dashboard/")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def _safe_get_json_list(url, params=None):
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def _date_key(date_str):
    if not date_str:
        return None
    try:
        return (
            datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
            .date()
            .isoformat()
        )
    except Exception:
        return None


def _resolved_customer_id(request):
    """Resolve customer_id and prevent payload spoofing when session token exists."""
    payload_customer_id = request.data.get("customer_id") if request.data else None
    claims = _auth_claims(request)
    token_customer_id = ""
    if claims.get("user_type") == "customer":
        token_customer_id = str(claims.get("sub") or "")
    session_customer_id = str(request.session.get("customer_id") or "")

    # If authenticated by token, reject mismatched payload customer_id.
    if token_customer_id and payload_customer_id:
        if str(payload_customer_id) != token_customer_id:
            return "", False

    resolved = (
        token_customer_id
        or (str(payload_customer_id) if payload_customer_id else "")
        or session_customer_id
    )
    return resolved, True


def _customer_has_purchased_book(customer_id, book_id):
    """Check if customer has at least one delivered/completed order item for book."""
    if not customer_id or not book_id:
        return False

    orders = _safe_get_json_list(
        f"{settings.ORDER_SERVICE_URL}/orders/", params={"customer_id": customer_id}
    )
    book_id_str = str(book_id)

    for order in orders:
        status_val = str(order.get("status", "")).lower()
        if status_val not in {"delivered", "completed"}:
            continue

        for item in order.get("items") or []:
            if str(item.get("book_id", "")) == book_id_str:
                return True

    return False


def _track_recommender_behaviour(
    customer_id,
    action_type,
    book_id=None,
    metadata=None,
    session_id="",
    search_query="",
):
    """Fire-and-forget tracking event to recommender service."""
    if not customer_id or not action_type:
        return

    payload = {
        "customer_id": str(customer_id),
        "action_type": str(action_type),
    }
    if book_id:
        payload["book_id"] = str(book_id)
    if session_id:
        payload["session_id"] = str(session_id)
    if search_query:
        payload["search_query"] = str(search_query)
    if isinstance(metadata, dict) and metadata:
        payload["metadata"] = metadata

    try:
        proxy_request(
            settings.RECOMMENDER_SERVICE_URL,
            "behaviours/",
            method="POST",
            data=payload,
        )
    except Exception as e:
        logger.warning("Failed to track recommender behaviour: %s", e)


# ============ Web UI Views ============


def home(request):
    """Home page"""
    return render(request, "home.html")


def books_page(request):
    """Books listing page"""
    query = (request.GET.get("q") or request.GET.get("search") or "").strip()
    bestseller_raw = (request.GET.get("bestseller") or "").strip().lower()
    bestseller_mode = bestseller_raw in {"1", "true", "yes", "on"}

    params = {}
    if query:
        params["search"] = query
    if bestseller_mode:
        params["ordering"] = "-total_sold"

    try:
        response = requests.get(
            f"{settings.BOOK_SERVICE_URL}/books/", params=params, timeout=10
        )
        books = response.json() if response.status_code == 200 else []
    except:
        books = []

    if bestseller_mode and isinstance(books, list):
        books = sorted(books, key=lambda b: int(b.get("total_sold") or 0), reverse=True)

    context = {
        "books": books,
        "initial_query": query,
        "bestseller_mode": bestseller_mode,
        "page_title": "Sách bán chạy" if bestseller_mode else "Khám phá sách",
        "page_subtitle": (
            "Danh sách sách có số lượt bán cao nhất"
            if bestseller_mode
            else "Tìm kiếm trong bộ sưu tập đa dạng với đủ thể loại"
        ),
    }

    return render(request, "books.html", context)


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
    role = _staff_session_role(request)
    if role:
        if _is_manager_role(role):
            return redirect("/manager/dashboard/")
        return redirect("/staff/dashboard/")
    return render(request, "staff_login.html")


def manager_login_page(request):
    """Manager login page"""
    role = _staff_session_role(request)
    if role:
        if _is_manager_role(role):
            return redirect("/manager/dashboard/")
        return redirect("/staff/dashboard/")
    return render(request, "manager_login.html")


@_role_required({"staff", "warehouse", "support"}, "/staff/login/")
def staff_dashboard_page(request):
    """Staff dashboard page"""
    return render(
        request,
        "staff_dashboard.html",
        {
            "admin_role": "staff",
            "active_nav": "staff-dashboard",
        },
    )


@_role_required({"manager", "admin"}, "/manager/login/")
def manager_dashboard_page(request):
    """Manager dashboard page"""
    return render(
        request,
        "manager_dashboard.html",
        {
            "admin_role": "manager",
            "active_nav": "manager-dashboard",
        },
    )


@_role_required({"staff", "warehouse", "support"}, "/staff/login/")
def staff_books_page(request):
    """Legacy staff books route -> inventory"""
    return redirect("/staff/inventory/")


@_role_required({"staff", "warehouse", "support"}, "/staff/login/")
def staff_customers_page(request):
    """Staff does not manage customers in split role model"""
    return redirect("/staff/dashboard/")


@_role_required({"staff", "warehouse", "support"}, "/staff/login/")
def staff_orders_page(request):
    """Staff orders management page"""
    return render(
        request,
        "staff_orders.html",
        {
            "admin_role": "staff",
            "active_nav": "staff-orders",
        },
    )


@_role_required({"staff", "warehouse", "support"}, "/staff/login/")
def staff_catalog_page(request):
    """Staff does not manage catalog in split role model"""
    return redirect("/staff/dashboard/")


@_role_required({"staff", "warehouse", "support"}, "/staff/login/")
def staff_inventory_page(request):
    """Staff inventory page"""
    return render(
        request,
        "staff_inventory.html",
        {
            "admin_role": "staff",
            "active_nav": "staff-inventory",
        },
    )


@_role_required({"staff", "warehouse", "support"}, "/staff/login/")
def staff_settings_page(request):
    """Staff settings page"""
    return render(
        request,
        "staff_settings.html",
        {
            "admin_role": "staff",
            "active_nav": "staff-settings",
        },
    )


@_role_required({"manager", "admin"}, "/manager/login/")
def manager_staffs_page(request):
    """Manager staffs management page"""
    return render(
        request,
        "manager_staffs.html",
        {
            "admin_role": "manager",
            "active_nav": "manager-staffs",
        },
    )


@_role_required({"manager", "admin"}, "/manager/login/")
def manager_inventory_page(request):
    """Manager inventory page"""
    return render(
        request,
        "manager_inventory.html",
        {
            "admin_role": "manager",
            "active_nav": "manager-inventory",
        },
    )


@_role_required({"manager", "admin"}, "/manager/login/")
def manager_store_page(request):
    """Manager store page"""
    return render(
        request,
        "manager_store.html",
        {
            "admin_role": "manager",
            "active_nav": "manager-store",
        },
    )


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

        if status_code in {200, 201} and not (
            isinstance(data, dict) and data.get("error")
        ):
            _track_recommender_behaviour(
                customer_id=customer_id,
                action_type="add_to_cart",
                book_id=request.data.get("book_id"),
                metadata={"source": "gateway_cart_api"},
            )

        return Response(data, status=status_code)


class CartItemAPI(APIView):
    """Proxy cart item API"""

    def put(self, request, customer_id, book_id):
        data, status_code = proxy_request(
            settings.CART_SERVICE_URL,
            f"carts/{customer_id}/items/{book_id}/",
            method="PUT",
            data=request.data,
        )
        return Response(data, status=status_code)

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

        if status_code in {200, 201} and isinstance(data, dict):
            customer_id = data.get("customer_id") or request.data.get("customer_id")
            order_id = data.get("order_id")
            for item in data.get("items") or []:
                book_id = item.get("book_id")
                if customer_id and book_id:
                    _track_recommender_behaviour(
                        customer_id=customer_id,
                        action_type="purchase",
                        book_id=book_id,
                        metadata={
                            "source": "gateway_order_api",
                            "order_id": str(order_id or ""),
                            "quantity": int(item.get("quantity") or 0),
                        },
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
            settings.AUTH_SERVICE_URL,
            "auth/customer/login/",
            method="POST",
            data=request.data,
        )
        if status_code == 200 and data and data.get("customer") and data.get("token"):
            request.session["jwt_token"] = data["token"]
            request.session["customer_id"] = data["customer"].get("customer_id")
        return Response(data, status=status_code)


class StaffLoginAPI(APIView):
    """Proxy staff login"""

    def post(self, request):
        payload = dict(request.data)
        payload["portal"] = "staff"
        data, status_code = proxy_request(
            settings.AUTH_SERVICE_URL,
            "auth/staff/login/",
            method="POST",
            data=payload,
        )
        if status_code == 200 and data and data.get("staff") and data.get("token"):
            role = (data["staff"].get("role") or "").lower()
            if _is_manager_role(role):
                return Response(
                    {
                        "error": "Manager/Admin account must login via /manager/login/",
                        "staff": data.get("staff"),
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            request.session["jwt_token"] = data["token"]
            request.session["staff_id"] = data["staff"].get("staff_id")
            request.session["staff_role"] = role
            request.session["staff_name"] = data["staff"].get("first_name")
        return Response(data, status=status_code)


class ManagerLoginAPI(APIView):
    """Proxy manager login"""

    def post(self, request):
        payload = dict(request.data)
        payload["portal"] = "manager"
        data, status_code = proxy_request(
            settings.AUTH_SERVICE_URL,
            "auth/staff/login/",
            method="POST",
            data=payload,
        )
        if status_code == 200 and data and data.get("staff") and data.get("token"):
            role = (data["staff"].get("role") or "").lower()
            if not _is_manager_role(role):
                return Response(
                    {
                        "error": "Only manager/admin can access manager portal",
                        "staff": data.get("staff"),
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            request.session["jwt_token"] = data["token"]
            request.session["staff_id"] = data["staff"].get("staff_id")
            request.session["staff_role"] = role
            request.session["staff_name"] = data["staff"].get("first_name")
        return Response(data, status=status_code)


class StaffSessionAPI(APIView):
    """Return current internal staff session status"""

    def get(self, request):
        claims = _auth_claims(request)
        if claims.get("user_type") != "staff":
            return Response({"authenticated": False})
        return Response(
            {
                "authenticated": True,
                "staff_id": claims.get("sub") or request.session.get("staff_id") or "",
                "role": claims.get("role") or request.session.get("staff_role") or "",
                "name": claims.get("name") or request.session.get("staff_name") or "",
            }
        )


class StaffLogoutAPI(APIView):
    """Clear internal staff session"""

    def post(self, request):
        token = request.session.get("jwt_token") or request.data.get("token")
        if token:
            proxy_request(
                settings.AUTH_SERVICE_URL,
                "auth/logout/",
                method="POST",
                data={"token": token},
            )
        _clear_auth_session(request)
        return Response({"success": True})


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


class RecommenderBehaviourAPI(APIView):
    """Proxy user behaviour tracking for recommender service."""

    ALLOWED_ACTIONS = {
        "view",
        "search",
        "click",
        "add_to_cart",
        "wishlist",
        "purchase",
        "share",
    }

    def post(self, request):
        payload = dict(request.data or {})
        action_type = str(payload.get("action_type") or "").strip().lower()
        if action_type not in self.ALLOWED_ACTIONS:
            return Response(
                {"error": "action_type không hợp lệ"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer_id, valid_identity = _resolved_customer_id(request)
        if not valid_identity:
            return Response(
                {"error": "customer_id không hợp lệ với tài khoản đăng nhập"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not customer_id:
            return Response(
                {"error": "customer_id là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized_payload = {
            "customer_id": customer_id,
            "action_type": action_type,
        }
        if payload.get("book_id"):
            normalized_payload["book_id"] = payload.get("book_id")
        if payload.get("session_id"):
            normalized_payload["session_id"] = payload.get("session_id")
        if payload.get("search_query"):
            normalized_payload["search_query"] = payload.get("search_query")
        metadata = payload.get("metadata")
        if isinstance(metadata, dict):
            normalized_payload["metadata"] = metadata

        data, status_code = proxy_request(
            settings.RECOMMENDER_SERVICE_URL,
            "behaviours/",
            method="POST",
            data=normalized_payload,
        )
        return Response(data, status=status_code)


class CustomersAPI(APIView):
    """Proxy customers API"""

    def get(self, request):
        data, status_code = proxy_request(settings.CUSTOMER_SERVICE_URL, "customers/")
        return Response(data, status=status_code)


class StaffMembersAPI(APIView):
    """Proxy staff members API"""

    def get(self, request):
        role = _staff_session_role(request)
        if not _is_manager_role(role):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        params = dict(request.query_params)
        params["include_inactive"] = "true"
        data, status_code = proxy_request(
            settings.STAFF_SERVICE_URL, "staff/", params=params
        )
        return Response(data, status=status_code)


class StaffUpdateAPI(APIView):
    """PATCH staff status/role/department — manager only"""

    def patch(self, request, staff_id):
        role = _staff_session_role(request)
        if not _is_manager_role(role):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        allowed_fields = {"is_active", "role", "department"}
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        data, status_code = proxy_request(
            settings.STAFF_SERVICE_URL,
            f"staff/{staff_id}/",
            method="PATCH",
            data=update_data,
        )
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
        customer_id, valid_identity = _resolved_customer_id(request)
        if not valid_identity:
            return Response(
                {"error": "customer_id không hợp lệ với tài khoản đăng nhập"},
                status=status.HTTP_403_FORBIDDEN,
            )

        book_id = request.data.get("book_id")
        if not customer_id or not book_id:
            return Response(
                {"error": "book_id và customer_id là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not _customer_has_purchased_book(customer_id, book_id):
            return Response(
                {"error": "Bạn chỉ có thể đánh giá những sách đã mua"},
                status=status.HTTP_403_FORBIDDEN,
            )

        payload = dict(request.data)
        payload["customer_id"] = customer_id
        data, status_code = proxy_request(
            settings.COMMENT_RATE_SERVICE_URL,
            "reviews/",
            method="POST",
            data=payload,
        )
        return Response(data, status=status_code)


class RatingsAPI(APIView):
    """Proxy ratings API"""

    def post(self, request):
        customer_id, valid_identity = _resolved_customer_id(request)
        if not valid_identity:
            return Response(
                {"error": "customer_id không hợp lệ với tài khoản đăng nhập"},
                status=status.HTTP_403_FORBIDDEN,
            )

        book_id = request.data.get("book_id")
        if not customer_id or not book_id:
            return Response(
                {"error": "book_id và customer_id là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not _customer_has_purchased_book(customer_id, book_id):
            return Response(
                {"error": "Bạn chỉ có thể đánh giá những sách đã mua"},
                status=status.HTTP_403_FORBIDDEN,
            )

        payload = dict(request.data)
        payload["customer_id"] = customer_id
        data, status_code = proxy_request(
            settings.COMMENT_RATE_SERVICE_URL,
            "ratings/",
            method="POST",
            data=payload,
        )
        return Response(data, status=status_code)


class StaffDashboardAggregateAPI(APIView):
    """Aggregate KPI for staff dashboard"""

    def get(self, request):
        role = _staff_session_role(request)
        if role not in {"staff", "warehouse", "support"}:
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        orders = _safe_get_json_list(f"{settings.ORDER_SERVICE_URL}/orders/")
        books = _safe_get_json_list(f"{settings.BOOK_SERVICE_URL}/books/")

        pending_statuses = {"pending", "confirmed", "processing", "shipped"}
        pending_orders = [
            o for o in orders if str(o.get("status", "")).lower() in pending_statuses
        ]

        total_inventory_units = sum(int(b.get("stock_quantity") or 0) for b in books)
        low_stock_books = [b for b in books if int(b.get("stock_quantity") or 0) <= 10]

        return Response(
            {
                "kpi": {
                    "total_orders": len(orders),
                    "pending_orders": len(pending_orders),
                    "inventory_units": total_inventory_units,
                    "book_titles": len(books),
                    "low_stock_books": len(low_stock_books),
                },
                "recent_orders": orders[:10],
                "inventory_preview": sorted(
                    books, key=lambda x: int(x.get("stock_quantity") or 0)
                )[:10],
            }
        )


class ManagerDashboardAggregateAPI(APIView):
    """Aggregate analytics for manager dashboard"""

    def get(self, request):
        role = _staff_session_role(request)
        if not _is_manager_role(role):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        orders = _safe_get_json_list(f"{settings.ORDER_SERVICE_URL}/orders/")
        payments = _safe_get_json_list(f"{settings.PAY_SERVICE_URL}/payments/")
        books = _safe_get_json_list(f"{settings.BOOK_SERVICE_URL}/books/")
        categories = _safe_get_json_list(f"{settings.CATALOG_SERVICE_URL}/categories/")
        authors = _safe_get_json_list(f"{settings.CATALOG_SERVICE_URL}/authors/")

        completed_payment_status = {"completed"}
        delivered_statuses = {"delivered", "completed"}
        successful_payments = [
            p
            for p in payments
            if str(p.get("status", "")).lower() in completed_payment_status
        ]

        order_by_id = {str(o.get("order_id")): o for o in orders}
        successful_order_ids = {
            str(p.get("order_id")) for p in successful_payments if p.get("order_id")
        }
        successful_orders = [
            o for o in orders if str(o.get("order_id")) in successful_order_ids
        ]
        completed_orders = [
            o for o in orders if str(o.get("status", "")).lower() in delivered_statuses
        ]

        revenue = sum(float(p.get("amount") or 0) for p in successful_payments)
        profit = revenue * 0.2
        pending_statuses = {"pending", "confirmed", "processing", "shipped"}
        pending_orders = [
            o for o in orders if str(o.get("status", "")).lower() in pending_statuses
        ]
        cancelled_orders = [
            o
            for o in orders
            if str(o.get("status", "")).lower() in {"cancelled", "refunded"}
        ]

        books_map = {str(b.get("book_id")): b for b in books}
        category_name_map = {
            str(c.get("category_id")): c.get("name") for c in categories
        }
        author_name_map = {str(a.get("author_id")): a.get("name") for a in authors}

        top_category_counter = defaultdict(int)
        top_book_qty = defaultdict(int)
        top_book_revenue = defaultdict(float)
        top_author_qty = defaultdict(int)

        for order in completed_orders:
            for item in order.get("items", []) or []:
                book_id = str(item.get("book_id") or "")
                qty = int(item.get("quantity") or 0)
                amount = float(item.get("total_price") or 0)
                top_book_qty[book_id] += qty
                top_book_revenue[book_id] += amount

                cat_id = str((books_map.get(book_id) or {}).get("category_id") or "")
                if cat_id:
                    top_category_counter[cat_id] += qty

                author_id = str((books_map.get(book_id) or {}).get("author_id") or "")
                if author_id:
                    top_author_qty[author_id] += qty

        top_categories = [
            {
                "category_id": cid,
                "category_name": category_name_map.get(cid, "Unknown"),
                "quantity": qty,
            }
            for cid, qty in sorted(
                top_category_counter.items(), key=lambda kv: kv[1], reverse=True
            )[:5]
        ]

        top_books = []
        for bid, qty in sorted(
            top_book_qty.items(), key=lambda kv: kv[1], reverse=True
        )[:10]:
            top_books.append(
                {
                    "book_id": bid,
                    "title": (books_map.get(bid) or {}).get("title", "Unknown"),
                    "quantity": qty,
                    "revenue": round(top_book_revenue.get(bid, 0.0), 2),
                }
            )

        top_authors = [
            {
                "author_id": aid,
                "author_name": author_name_map.get(aid, "Unknown"),
                "quantity": qty,
            }
            for aid, qty in sorted(
                top_author_qty.items(), key=lambda kv: kv[1], reverse=True
            )[:8]
        ]

        revenue_by_day = defaultdict(float)
        for payment in successful_payments:
            day = _date_key(payment.get("paid_at") or payment.get("created_at"))
            if day:
                revenue_by_day[day] += float(payment.get("amount") or 0)
        revenue_timeline = [
            {"date": d, "revenue": round(v, 2)}
            for d, v in sorted(revenue_by_day.items())
        ]

        buy_by_day = defaultdict(int)
        for order in completed_orders:
            day = _date_key(order.get("order_date") or order.get("created_at"))
            if day:
                buy_by_day[day] += 1

        behaviour_timeline = []
        today = datetime.now().date()
        for i in range(13, -1, -1):
            day = (today - timedelta(days=i)).isoformat()
            buy = buy_by_day.get(day, 0)
            behaviour_timeline.append(
                {
                    "date": day,
                    "view": buy * 7 + (i % 3),
                    "search": buy * 4 + (i % 2),
                    "add": buy * 2 + (i % 2),
                    "buy": buy,
                }
            )

        recent_transactions = []
        for payment in sorted(
            successful_payments,
            key=lambda p: str(p.get("paid_at") or p.get("created_at") or ""),
            reverse=True,
        )[:10]:
            order = order_by_id.get(str(payment.get("order_id")), {})
            recent_transactions.append(
                {
                    "payment_id": payment.get("payment_id"),
                    "order_id": payment.get("order_id"),
                    "order_number": order.get("order_number"),
                    "customer_id": order.get("customer_id"),
                    "amount": payment.get("amount", 0),
                    "status": payment.get("status"),
                    "order_status": order.get("status"),
                    "paid_at": payment.get("paid_at") or payment.get("created_at"),
                }
            )

        return Response(
            {
                "kpi": {
                    "total_revenue": round(revenue, 2),
                    "profit": round(profit, 2),
                    "total_orders": len(orders),
                    "pending_orders": len(pending_orders),
                    "completed_orders": len(completed_orders),
                    "cancelled_orders": len(cancelled_orders),
                },
                "charts": {
                    "top_categories": top_categories,
                    "top_authors": top_authors,
                    "top_books": top_books,
                    "behaviour_timeline": behaviour_timeline,
                },
                "recent_transactions": recent_transactions,
                "meta": {
                    "behaviour_source": "mock_schema_compatible",
                    "revenue_rule": "completed_payments_only",
                    "top_rule": "completed_or_delivered_orders_only",
                },
            }
        )


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
