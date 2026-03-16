# BookStore Microservice - Tiến Độ Thực Hiện

## 📋 Tổng Quan Dự Án

Chuyển đổi hệ thống **BookStore Monolithic** sang kiến trúc **Microservices** theo yêu cầu Assignment 05 & 06.

### Nguồn gốc từ Monolithic
- **Vị trí**: `BookStore_Mono/bookstore/`
- **Apps gốc**: accounts, books, cart, orders, payments, shipping, reviews, recommendations, inventory, promotions, cms, support, wishlists

---

## 🎯 Danh sách 12 Services cần triển khai (Assignment 05)

| # | Service | Port | Mô tả | Trạng thái |
|---|---------|------|-------|------------|
| 1 | customer-service | 8001 | Quản lý thông tin khách hàng | ✅ Hoàn thành |
| 2 | staff-service | 8002 | Quản lý nhân viên | ✅ Hoàn thành |
| 3 | catalog-service | 8004 | Quản lý danh mục, category, author, publisher | ✅ Hoàn thành |
| 4 | book-service | 8005 | Quản lý sách | ✅ Hoàn thành |
| 5 | cart-service | 8006 | Giỏ hàng | ✅ Hoàn thành |
| 6 | order-service | 8007 | Đơn hàng | ✅ Hoàn thành |
| 7 | pay-service | 8008 | Thanh toán | ✅ Hoàn thành |
| 8 | ship-service | 8009 | Vận chuyển | ✅ Hoàn thành |
| 9 | comment-rate-service | 8010 | Đánh giá & bình luận | ✅ Hoàn thành |
| 10 | recommender-ai-service | 8011 | Gợi ý sách AI | ✅ Hoàn thành |
| 11 | api-gateway | 8000 | Gateway & Web Interface | ✅ Hoàn thành |
| 12 | docker-compose.yml | - | Orchestration | ✅ Hoàn thành |

---

## 📁 Cấu trúc dự án

```
bookstore-micro052/
├── customer-service/       # Port 8001
├── staff-service/          # Port 8002
├── manager-service/        # Port 8003
├── catalog-service/        # Port 8004
├── book-service/           # Port 8005
├── cart-service/           # Port 8006
├── order-service/          # Port 8007
├── pay-service/            # Port 8008
├── ship-service/           # Port 8009
├── comment-rate-service/   # Port 8010
├── recommender-ai-service/ # Port 8011
├── api-gateway/            # Port 8000
├── docker-compose.yml
└── BookStore_Mono/         # Bản monolithic gốc
```

---

## 📊 Mapping Monolithic → Microservices

| Monolithic App | → | Microservice |
|----------------|---|--------------|
| accounts (Customer) | → | customer-service |
| accounts (Staff) | → | staff-service |
| accounts (User/Admin) | → | manager-service |
| books (Category, Author, Publisher) | → | catalog-service |
| books (Book) | → | book-service |
| cart | → | cart-service |
| orders | → | order-service |
| payments | → | pay-service |
| shipping | → | ship-service |
| reviews | → | comment-rate-service |
| recommendations | → | recommender-ai-service |

---

## 🔄 Luồng giao tiếp giữa các services

### 1. Customer Registration Flow
```
POST /customers/ → customer-service
    → call cart-service POST /carts/ (tự động tạo cart)
```

### 2. Add to Cart Flow
```
POST /cart-items/ → cart-service
    → call book-service GET /books/{id}/ (kiểm tra sách tồn tại)
    → if exists → add item
```

### 3. Order Flow
```
POST /orders/ → order-service
    → call cart-service GET /carts/{customer_id}/
    → call pay-service POST /payments/
    → call ship-service POST /shippings/
```

---

## 📝 Nhật ký thực hiện

### Ngày 04/03/2026

#### ✅ Phân tích hệ thống Monolithic
- Đã xem xét cấu trúc `BookStore_Mono/bookstore/apps/`
- Xác định các models chính:
  - **accounts**: User, Customer, Staff (360 dòng)
  - **books**: Publisher, Author, BookLanguage, BookFormat, BookSeries, Book, Category, Tag (385 dòng)
  - **cart**: Cart, CartItem
  - **orders**: Order, OrderItem (151 dòng)
  - **payments**: Payment, PaymentTransaction, Refund (177 dòng)
  - **shipping**: Shipping, Shipment, Address (185 dòng)
  - **reviews**: Review, Rating
  - **recommendations**: RecommendationEngine, PurchaseHistory, UserBehaviour (189 dòng)
  - **inventory**: Warehouse, Inventory, InventoryItem, StockLog (346 dòng)
  - **promotions**: Discount, Coupon

#### 🔄 Bắt đầu tạo microservices
- Tạo file progress.md để theo dõi tiến độ
- Chuẩn bị tạo 12 services theo yêu cầu PDF

---

## 🛠️ Công nghệ sử dụng

- **Framework**: Django REST Framework
- **Database**: SQLite (mỗi service riêng biệt)
- **Container**: Docker & Docker Compose
- **Communication**: REST API (inter-service calls)

---

## 📌 Yêu cầu chức năng (Functional Requirements)

1. ✅ Customer registration tự động tạo cart
2. ✅ Staff quản lý sách
3. ✅ Customer thêm sách vào cart, xem cart, update cart
4. ✅ Order kích hoạt payment và shipping
5. ✅ Customer có thể rate sách

---

## 🎉 HOÀN THÀNH Assignment 05

### Các services đã triển khai:

#### 1. customer-service (Port 8001)
- Models: Customer
- APIs: CRUD customers, login, logout, verify token
- Inter-service: Tự động tạo cart khi đăng ký

#### 2. staff-service (Port 8002)
- Models: Staff, StaffSession
- APIs: CRUD staff, login/logout, token verification

#### 3. catalog-service (Port 8004)
- Models: Publisher, Author, Category, Tag, BookLanguage, BookFormat
- APIs: CRUD cho tất cả entities

#### 4. book-service (Port 8005)
- Models: Book
- APIs: CRUD books, search, filter

#### 5. cart-service (Port 8006)
- Models: Cart, CartItem
- APIs: CRUD cart, add/remove items, calculate total
- Inter-service: Validate book từ book-service

#### 6. order-service (Port 8007)
- Models: Order, OrderItem
- APIs: CRUD orders
- Inter-service: Lấy cart, tạo payment, tạo shipping

#### 7. pay-service (Port 8008)
- Models: Payment, PaymentTransaction, Refund
- APIs: Create payment, process, refund

#### 8. ship-service (Port 8009)
- Models: Shipping
- APIs: Create shipping, update status, track

#### 9. comment-rate-service (Port 8010)
- Models: Review, Rating
- APIs: CRUD reviews/ratings
- Inter-service: Update book rating

#### 10. recommender-ai-service (Port 8011)
- Models: RecommendationEngine, UserBehaviour, Recommendation
- APIs: Track behaviour, get recommendations

#### 11. api-gateway (Port 8000)
- Web templates: home, books, cart, login, register
- API proxy to all services
- Health check aggregation

### Chạy project:
```bash
docker-compose up --build
```

Truy cập: http://localhost:8000

---
python3 seed_data.py

## 📦 Deliverables (Assignment 05)

1. [ ] GitHub repository
2. [x] Architecture diagram cho mỗi service
3. [x] API documentation
4. [ ] 10-minute demo video
5. [ ] 8-12 page technical report

---
