# BookStore Microservices - API Documentation

## 1) Tổng quan

Tài liệu này mô tả API của hệ thống BookStore Microservices theo code hiện tại trong workspace.

- Kiến trúc: RESTful API, JSON
- Gateway public: `http://localhost:8000`
- Các service chạy độc lập qua Docker Compose
- Mỗi service có endpoint health check: `GET /health/`

---

## 2) Base URL theo service

| Service | Host Port | Base URL |
|---|---:|---|
| API Gateway | 8000 | `http://localhost:8000` |
| customer-service | 8001 | `http://localhost:8001` |
| staff-service | 8002 | `http://localhost:8002` |
| auth-service | 8003 | `http://localhost:8003` |
| catalog-service | 8004 | `http://localhost:8004` |
| book-service | 8005 | `http://localhost:8005` |
| cart-service | 8006 | `http://localhost:8006` |
| order-service | 8007 | `http://localhost:8007` |
| pay-service | 8008 | `http://localhost:8008` |
| ship-service | 8009 | `http://localhost:8009` |
| comment-rate-service | 8010 | `http://localhost:8010` |
| recommender-ai-service | 8011 | `http://localhost:8011` |

---

## 3) Quy ước chung

### 3.1 Headers

```http
Content-Type: application/json
Accept: application/json
```

### 3.2 HTTP Status thường dùng

- `200 OK`: Thành công
- `201 Created`: Tạo mới thành công
- `204 No Content`: Xóa thành công
- `400 Bad Request`: Dữ liệu đầu vào không hợp lệ
- `401 Unauthorized`: Sai thông tin đăng nhập/token không hợp lệ
- `404 Not Found`: Không tìm thấy tài nguyên
- `503 Service Unavailable`: Service phụ trợ đang lỗi/timeout

### 3.3 Kiểu định danh

- Hầu hết tài nguyên chính dùng `UUID` (customer_id, book_id, order_id, ...)

---

## 4) API Gateway (Public APIs)

> Dùng cho frontend/web client. Gateway sẽ proxy sang các microservice tương ứng.

### 4.1 Authentication

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/api/auth/login/` | Đăng nhập customer |
| POST | `/api/auth/staff/login/` | Đăng nhập staff |
| POST | `/api/auth/manager/login/` | Đăng nhập manager |
| GET | `/api/auth/staff/session/` | Kiểm tra session staff/manager |
| POST | `/api/auth/staff/logout/` | Đăng xuất staff/manager |
| POST | `/api/auth/register/` | Đăng ký customer |

### 4.2 Books

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/books/` | Danh sách sách (hỗ trợ query filter) |
| POST | `/api/books/` | Tạo sách |
| GET | `/api/books/{book_id}/` | Chi tiết sách |
| PUT | `/api/books/{book_id}/` | Cập nhật sách |
| DELETE | `/api/books/{book_id}/` | Xóa sách |

### 4.3 Cart

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/cart/{customer_id}/` | Lấy giỏ hàng theo customer |
| POST | `/api/cart/{customer_id}/` | Thêm item vào cart |
| DELETE | `/api/cart/{customer_id}/items/{book_id}/` | Xóa item khỏi cart |

### 4.4 Orders

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/orders/` | Lấy tất cả đơn |
| GET | `/api/orders/{customer_id}/` | Lấy đơn theo customer (proxy query param) |
| POST | `/api/orders/` | Tạo đơn hàng |
| GET | `/api/orders/{order_id}/detail/` | Chi tiết đơn |
| PUT | `/api/orders/{order_id}/detail/` | Cập nhật trạng thái đơn |
| POST | `/api/orders/{order_id}/cancel/` | Hủy đơn |

### 4.5 Catalog/Admin & Reviews

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/customers/` | Danh sách khách hàng |
| GET | `/api/staffs/` | Danh sách staff |
| PATCH | `/api/staffs/{staff_id}/` | Cập nhật staff (role/is_active/department) |
| GET | `/api/categories/` | Danh sách category |
| GET | `/api/authors/` | Danh sách author |
| GET | `/api/publishers/` | Danh sách publisher |
| GET | `/api/tags/` | Danh sách tag |
| GET | `/api/dashboard/staff/` | Aggregate dashboard cho staff portal |
| GET | `/api/dashboard/manager/` | Aggregate KPI/charts cho manager portal |
| GET | `/api/reviews/` | Danh sách review |
| POST | `/api/reviews/` | Tạo review |
| POST | `/api/ratings/` | Tạo/cập nhật rating |

### 4.6 Recommendations

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/recommendations/{customer_id}/` | Lấy gợi ý sách |

### 4.7 Health

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/health/` | Health của gateway + trạng thái các service |

---

## 5) customer-service (Port 8001)

### Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/customers/` | Danh sách customer |
| POST | `/customers/` | Tạo customer (tự gọi cart-service tạo cart) |
| GET | `/customers/{customer_id}/` | Chi tiết customer |
| PUT | `/customers/{customer_id}/` | Cập nhật customer |
| DELETE | `/customers/{customer_id}/` | Xóa customer |
| POST | `/customers/{customer_id}/loyalty/` | Cộng loyalty points |
| POST | `/login/` | Đăng nhập customer |
| POST | `/logout/` | Đăng xuất customer |
| GET | `/health/` | Health check |

### Request mẫu - tạo customer

```json
{
  "username": "demo_user",
  "email": "demo@bookstore.com",
  "password_hash": "demo123",
  "first_name": "Demo",
  "last_name": "User",
  "phone_number": "0900000000",
  "date_of_birth": "2000-01-01",
  "gender": "other"
}
```

### Response mẫu - login

```json
{
  "token": "<token>",
  "customer": {
    "customer_id": "uuid",
    "email": "demo@bookstore.com",
    "first_name": "Demo",
    "last_name": "User"
  }
}
```

---

## 6) staff-service (Port 8002)

### Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/staff/` | Danh sách staff (filter: `role`, `department`) |
| POST | `/staff/` | Tạo staff |
| GET | `/staff/{staff_id}/` | Chi tiết staff |
| PUT | `/staff/{staff_id}/` | Cập nhật staff |
| DELETE | `/staff/{staff_id}/` | Soft delete (is_active=false) |
| POST | `/login/` | Đăng nhập staff |
| POST | `/logout/` | Đăng xuất staff |
| POST | `/verify/` | Xác thực token staff |
| GET | `/health/` | Health check |

---

## 7) auth-service (Port 8003)

### Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/auth/customer/login/` | Đăng nhập customer, trả JWT |
| POST | `/auth/staff/login/` | Đăng nhập staff/manager, trả JWT |
| POST | `/auth/verify/` | Verify JWT, hỗ trợ kiểm tra role |
| POST | `/auth/logout/` | Stateless logout |
| GET | `/health/` | Health check |

### JWT claims chính

- `sub`
- `user_type`
- `role`
- `name`
- `email`
- `iat`
- `exp`

---

## 8) catalog-service (Port 8004)

### Endpoints chính

| Resource | List/Create | Detail |
|---|---|---|
| Publisher | `GET,POST /publishers/` | `GET,PUT,DELETE /publishers/{publisher_id}/` |
| Author | `GET,POST /authors/` | `GET,PUT,DELETE /authors/{author_id}/` |
| Category | `GET,POST /categories/` | `GET,PUT,DELETE /categories/{category_id}/` |
| Tag | `GET,POST /tags/` | `GET,PUT,DELETE /tags/{tag_id}/` |
| Language | `GET,POST /languages/` | - |
| Format | `GET,POST /formats/` | - |

### Query params

- `/authors/?search=<keyword>`
- `/categories/?root=true` (chỉ lấy category gốc)

---

## 9) book-service (Port 8005)

### Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/books/` | Danh sách sách + filter/search/order |
| POST | `/books/` | Tạo sách |
| GET | `/books/{book_id}/` | Chi tiết sách |
| PUT | `/books/{book_id}/` | Cập nhật sách |
| PATCH | `/books/{book_id}/` | Partial update |
| DELETE | `/books/{book_id}/` | Xóa sách |
| GET | `/books/{book_id}/stock/` | Kiểm tra tồn kho |
| POST | `/books/{book_id}/stock/` | Cập nhật tồn kho |
| POST | `/books/{book_id}/rating/` | Đồng bộ rating từ review-service |
| POST | `/books/{book_id}/sales/` | Đồng bộ total_sold |
| GET | `/health/` | Health check |

### Query params `/books/`

- `status`
- `category_id`
- `author_id`
- `search`
- `featured=true`
- `bestseller=true`
- `ordering` (mặc định `-created_at`)

### Request mẫu - update stock

```json
{
  "quantity_change": -2
}
```

---

## 10) cart-service (Port 8006)

### Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/carts/` | Danh sách cart active |
| POST | `/carts/` | Tạo cart (nếu đã có cart active thì trả cart cũ) |
| GET | `/carts/{customer_id}/` | Lấy cart theo customer (auto-create nếu chưa có) |
| DELETE | `/carts/{customer_id}/` | Deactivate cart |
| POST | `/carts/{customer_id}/items/` | Thêm item vào cart |
| PUT | `/carts/{customer_id}/items/{book_id}/` | Cập nhật quantity item |
| DELETE | `/carts/{customer_id}/items/{book_id}/` | Xóa item khỏi cart |
| POST | `/carts/{customer_id}/clear/` | Xóa toàn bộ item trong cart |
| GET | `/health/` | Health check |

### Request mẫu - add item

```json
{
  "book_id": "<uuid>",
  "quantity": 1
}
```

### Lưu ý nghiệp vụ

- Service gọi `book-service` để xác thực sách tồn tại và kiểm tra tồn kho.
- Có thể trả `503` nếu không gọi được `book-service`.

---

## 11) order-service (Port 8007)

### Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/orders/` | Danh sách order (hỗ trợ `?customer_id=`) |
| POST | `/orders/` | Tạo order từ cart |
| GET | `/orders/{order_id}/` | Chi tiết order |
| PUT | `/orders/{order_id}/` | Cập nhật status order |
| DELETE | `/orders/{order_id}/` | Xóa order (chỉ pending/cancelled) |
| POST | `/orders/{order_id}/cancel/` | Hủy order (chỉ pending/confirmed) |
| GET | `/health/` | Health check |

### Request mẫu - create order

```json
{
  "customer_id": "<uuid>",
  "shipping_address": "Hà Nội",
  "billing_address": "Hà Nội",
  "shipping_method": "standard",
  "payment_method": "cod",
  "notes": "Giao giờ hành chính"
}
```

### Luồng nội bộ khi tạo order

1. Gọi cart-service lấy cart items
2. Tạo order + order items
3. Đồng bộ sales về book-service qua `POST /books/{book_id}/sales/`
4. Gọi pay-service tạo payment
5. Gọi ship-service tạo shipping
6. Clear cart

### Lưu ý trạng thái ảnh hưởng total_sold

- Chuyển sang `cancelled/refunded`: giảm total_sold.
- Chuyển từ `cancelled/refunded` về trạng thái active: cộng lại total_sold.

---

## 12) pay-service (Port 8008)

### Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/payments/` | Danh sách payment (filter `?order_id=`) |
| POST | `/payments/` | Tạo payment |
| GET | `/payments/{payment_id}/` | Chi tiết payment |
| POST | `/payments/{payment_id}/process/` | Xử lý payment (pending -> completed) |
| POST | `/refunds/` | Tạo refund |
| GET | `/health/` | Health check |

### Request mẫu - create payment

```json
{
  "order_id": "<uuid>",
  "payment_method": "cod",
  "amount": 158000,
  "currency": "VND"
}
```

### Request mẫu - refund

```json
{
  "payment_id": "<uuid>",
  "amount": 158000,
  "reason": "Customer request"
}
```

---

## 13) ship-service (Port 8009)

### Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/shippings/` | Danh sách shipping (filter `?order_id=`) |
| POST | `/shippings/` | Tạo shipping |
| GET | `/shippings/{shipping_id}/` | Chi tiết shipping |
| PUT | `/shippings/{shipping_id}/status/` | Cập nhật trạng thái shipping |
| GET | `/track/{tracking_code}/` | Tra cứu vận đơn |
| GET | `/health/` | Health check |

### Request mẫu - create shipping

```json
{
  "order_id": "<uuid>",
  "shipping_method": "standard",
  "carrier": "GHTK",
  "shipping_address": "Hồ Chí Minh"
}
```

### Request mẫu - update status

```json
{
  "status": "delivered"
}
```

---

## 14) comment-rate-service (Port 8010)

### Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/reviews/` | Danh sách review (`book_id`, `customer_id`) |
| POST | `/reviews/` | Tạo review (có thể kèm `score`) |
| GET | `/reviews/{review_id}/` | Chi tiết review |
| PUT | `/reviews/{review_id}/` | Cập nhật review |
| DELETE | `/reviews/{review_id}/` | Xóa review |
| POST | `/reviews/{review_id}/helpful/` | Tăng helpful_count |
| GET | `/ratings/` | Danh sách rating (`book_id`) |
| POST | `/ratings/` | Tạo/cập nhật rating |
| GET | `/books/{book_id}/rating-summary/` | Tổng hợp rating theo sách |
| GET | `/health/` | Health check |

### Request mẫu - create review

```json
{
  "book_id": "<uuid>",
  "customer_id": "<uuid>",
  "order_item_id": "<uuid>",
  "title": "Sách hay",
  "content": "Nội dung rất hữu ích",
  "is_verified_purchase": true,
  "score": 5
}
```

### Request mẫu - create/update rating

```json
{
  "book_id": "<uuid>",
  "customer_id": "<uuid>",
  "score": 4
}
```

### Lưu ý nghiệp vụ

- Sau khi tạo/cập nhật rating/review, service đồng bộ `average_rating` về book-service qua `POST /books/{book_id}/rating/`.

---

## 15) recommender-ai-service (Port 8011)

### Endpoints

| Method | Endpoint | Mô tả |
|---|---|---|
| POST | `/behaviours/` | Track hành vi user |
| GET | `/recommendations/{customer_id}/` | Lấy gợi ý sách (`?limit=`) |
| GET | `/popular/` | Sách phổ biến theo tương tác (`?limit=`) |
| GET | `/history/{customer_id}/` | Lịch sử hành vi user |
| GET | `/engines/` | Danh sách engine |
| POST | `/engines/` | Tạo engine |
| GET | `/health/` | Health check |

### Request mẫu - track behaviour

```json
{
  "customer_id": "<uuid>",
  "book_id": "<uuid>",
  "action_type": "view",
  "session_id": "sess_001",
  "search_query": "python",
  "metadata": {
    "source": "home_page"
  }
}
```

---

## 16) End-to-End API Flows (đưa vào báo cáo)

### 16.1 Đăng ký customer

1. `POST /customers/` (customer-service)
2. customer-service gọi `POST /carts/` (cart-service) để auto tạo cart

### 16.2 Thêm sách vào giỏ

1. `POST /carts/{customer_id}/items/` (cart-service)
2. cart-service gọi `GET /books/{book_id}/` (book-service) để validate

### 16.3 Checkout tạo đơn hàng

1. `POST /orders/` (order-service)
2. order-service gọi cart-service lấy item
3. đồng bộ sales sang book-service
4. gọi pay-service tạo payment
5. gọi ship-service tạo shipping
6. clear cart

### 16.4 Rating đồng bộ về Book

1. `POST /ratings/` hoặc `POST /reviews/` (comment-rate-service)
2. comment-rate-service tính lại average
3. gọi `POST /books/{book_id}/rating/` (book-service)

---

## 17) cURL mẫu nhanh

### Login customer qua gateway

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@bookstore.com","password":"demo123"}'
```

### Lấy books

```bash
curl "http://localhost:8005/books/?search=python&ordering=-created_at"
```

### Add to cart

```bash
curl -X POST http://localhost:8006/carts/<customer_id>/items/ \
  -H "Content-Type: application/json" \
  -d '{"book_id":"<book_uuid>","quantity":1}'
```

### Create order

```bash
curl -X POST http://localhost:8007/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id":"<customer_uuid>",
    "shipping_address":"Hà Nội",
    "billing_address":"Hà Nội",
    "payment_method":"cod",
    "shipping_method":"standard"
  }'
```

---

## 18) Ghi chú triển khai

- Authentication đã chuyển sang `auth-service` dùng JWT; Gateway verify token/role cho API quản trị.
- Một số API có logic soft-delete (`is_active=false`) thay vì hard-delete.
- Gateway có một số endpoint proxy dành cho UI staff/customer song song với endpoint service trực tiếp.
- Khi viết báo cáo, nên đặt API Gateway làm điểm truy cập chính cho client, và mô tả inter-service call ở phần sequence diagrams.
