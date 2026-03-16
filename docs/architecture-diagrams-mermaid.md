# BookStore Microservices - Architecture Diagrams

## 📐 1. Tổng Quan Kiến Trúc Hệ Thống (System Architecture)

```mermaid
flowchart TB
    subgraph CLIENT["🖥️ CLIENT LAYER"]
        Browser["🌐 Browser"]
        Mobile["📱 Mobile App"]
        Admin["👨‍💼 Admin UI"]
        API["🔌 REST API"]
    end

    subgraph GATEWAY["🚪 API GATEWAY (Port 8000)"]
        Routing["Routing & Load Balancing"]
        Auth["Authentication & Authorization"]
        Transform["Request/Response Transformation"]
        RateLimit["Rate Limiting & Caching"]
        WebUI["Web UI Templates (Django)"]
    end

    subgraph USER["👤 USER DOMAIN"]
        CustomerSvc["customer-service<br/>Port: 8001"]
        StaffSvc["staff-service<br/>Port: 8002"]
    end

    subgraph PRODUCT["📚 PRODUCT DOMAIN"]
        CatalogSvc["catalog-service<br/>Port: 8004"]
        BookSvc["book-service<br/>Port: 8005"]
    end

    subgraph ORDER["🛒 ORDER DOMAIN"]
        CartSvc["cart-service<br/>Port: 8006"]
        OrderSvc["order-service<br/>Port: 8007"]
        PaySvc["pay-service<br/>Port: 8008"]
        ShipSvc["ship-service<br/>Port: 8009"]
    end

    subgraph ANALYTICS["📊 ANALYTICS DOMAIN"]
        CommentSvc["comment-rate-service<br/>Port: 8010"]
        RecommendSvc["recommender-ai-service<br/>Port: 8011"]
    end

    Browser --> GATEWAY
    Mobile --> GATEWAY
    Admin --> GATEWAY
    API --> GATEWAY

    GATEWAY --> USER
    GATEWAY --> PRODUCT
    GATEWAY --> ORDER
    GATEWAY --> ANALYTICS
```

---

## 📐 2. Chi Tiết Kiến Trúc Từng Service

### 2.1 Customer Service (Port 8001)

```mermaid
flowchart TB
    subgraph CustomerService["🧑‍💼 CUSTOMER SERVICE - Port 8001"]
        subgraph API_Layer["API Layer"]
            Login["/login/"]
            Register["/register/"]
            Customers["/customers/"]
        end

        subgraph Business["Business Logic"]
            B1["Customer Registration"]
            B2["Authentication (Login/Logout)"]
            B3["Profile Management"]
            B4["Password Hashing"]
        end

        subgraph Data["Data Layer"]
            subgraph CustomerModel["Customer Model"]
                F1["customer_id (UUID)"]
                F2["email, phone_number"]
                F3["first_name, last_name"]
                F4["password_hash"]
                F5["is_active, is_verified"]
            end
            DB[(SQLite DB<br/>customer.db)]
        end

        API_Layer --> Business
        Business --> Data
        CustomerModel --> DB
    end

    subgraph External["External Communications"]
        CartSvc["cart-service<br/>(8006)"]
        OrderSvc["order-service<br/>(8007)"]
    end

    CustomerService -->|"Auto create cart<br/>on register"| CartSvc
    CustomerService -.->|"Get customer info"| OrderSvc
```

### 2.2 Staff Service (Port 8002)

```mermaid
flowchart TB
    subgraph StaffService["👨‍💻 STAFF SERVICE - Port 8002"]
        subgraph API_Layer["API Layer"]
            Login["/login/"]
            Logout["/logout/"]
            Staff["/staff/"]
        end

        subgraph Business["Business Logic"]
            B1["Staff Registration"]
            B2["Session Management"]
            B3["Role-based Access Control"]
            B4["Token Verification"]
        end

        subgraph Data["Data Layer"]
            subgraph StaffModel["Staff Model"]
                F1["staff_id"]
                F2["email, role"]
                F3["department"]
            end
            subgraph SessionModel["StaffSession Model"]
                S1["session_token"]
                S2["staff (FK)"]
                S3["expires_at"]
            end
            DB[(SQLite DB<br/>staff.db)]
        end

        API_Layer --> Business
        Business --> Data
        StaffModel --> DB
        SessionModel --> DB
    end
```

### 2.3 Catalog Service (Port 8004)

```mermaid
flowchart TB
    subgraph CatalogService["📑 CATALOG SERVICE - Port 8004"]
        subgraph API_Layer["API Layer"]
            Publishers["/publishers/"]
            Authors["/authors/"]
            Categories["/categories/"]
            Tags["/tags/"]
            Formats["/formats/"]
        end

        subgraph Data["Data Layer"]
            subgraph Models["Models"]
                Publisher["Publisher<br/>• name<br/>• website<br/>• country"]
                Author["Author<br/>• name<br/>• bio<br/>• nationality"]
                Category["Category<br/>• name<br/>• slug<br/>• parent"]
                Tag["Tag<br/>• name<br/>• slug"]
                Format["BookFormat<br/>• name<br/>• description"]
            end
            DB[(SQLite DB<br/>catalog.db)]
        end

        API_Layer --> Data
        Models --> DB
    end

    BookSvc["book-service<br/>(8005)"]
    CatalogService -->|"Get author,<br/>category info"| BookSvc
```

### 2.4 Book Service (Port 8005)

```mermaid
flowchart TB
    subgraph BookService["📚 BOOK SERVICE - Port 8005"]
        subgraph API_Layer["API Layer"]
            GetBooks["GET /books/"]
            PostBooks["POST /books/"]
            GetBook["GET /books/{id}/"]
            PutBook["PUT /books/{id}/"]
            DeleteBook["DELETE /books/{id}/"]
        end

        subgraph Data["Data Layer"]
            subgraph BookModel["Book Model"]
                F1["book_id (UUID), isbn"]
                F2["title, description"]
                F3["price, stock_quantity"]
                F4["author_id (FK), publisher_id"]
                F5["category_id, cover_image_url"]
                F6["average_rating, total_sold"]
                F7["is_bestseller, is_featured"]
            end
            DB[(SQLite DB<br/>book.db)]
        end

        API_Layer --> Data
        BookModel --> DB
    end

    subgraph External["External Communications"]
        CartSvc["cart-service<br/>(8006)"]
        OrderSvc["order-service<br/>(8007)"]
        CommentSvc["comment-rate<br/>(8010)"]
    end

    CartSvc -->|"Validate book,<br/>get price"| BookService
    OrderSvc -->|"Get book info"| BookService
    CommentSvc -->|"Update<br/>average_rating"| BookService
```

### 2.5 Cart Service (Port 8006)

```mermaid
flowchart TB
    subgraph CartService["🛒 CART SERVICE - Port 8006"]
        subgraph API_Layer["API Layer"]
            GetCart["GET /carts/{customer_id}/"]
            PostItem["POST /carts/{customer_id}/items/"]
            PutItem["PUT /carts/{customer_id}/items/{book_id}/"]
            DeleteItem["DELETE /carts/{customer_id}/items/{book_id}/"]
        end

        subgraph Business["Business Logic"]
            B1["Auto-create cart on customer registration"]
            B2["Add/Remove items"]
            B3["Update quantities"]
            B4["Calculate totals"]
            B5["Validate stock availability"]
        end

        subgraph Data["Data Layer"]
            subgraph CartModel["Cart Model"]
                C1["cart_id"]
                C2["customer_id"]
                C3["is_active"]
                C4["created_at"]
            end
            subgraph CartItemModel["CartItem Model"]
                CI1["cart_item_id"]
                CI2["cart (FK)"]
                CI3["book_id"]
                CI4["quantity"]
                CI5["unit_price"]
            end
            DB[(SQLite DB<br/>cart.db)]
        end

        API_Layer --> Business
        Business --> Data
        CartModel --> DB
        CartItemModel --> DB
    end

    BookSvc["book-service<br/>(8005)"]
    OrderSvc["order-service<br/>(8007)"]

    CartService -->|"Validate book<br/>Get price/stock"| BookSvc
    OrderSvc -->|"Get cart items<br/>for order"| CartService
```

### 2.6 Order Service (Port 8007)

```mermaid
flowchart TB
    subgraph OrderService["📦 ORDER SERVICE - Port 8007"]
        subgraph API_Layer["API Layer"]
            GetOrders["GET /orders/"]
            GetByCustomer["GET /orders/?customer_id=..."]
            PostOrder["POST /orders/"]
            GetOrder["GET /orders/{order_id}/"]
            CancelOrder["POST /orders/{order_id}/cancel/"]
        end

        subgraph Business["Business Logic - Order Creation Flow"]
            B1["1. Get cart items from cart-service"]
            B2["2. Calculate totals (subtotal, tax, ship)"]
            B3["3. Create payment via pay-service"]
            B4["4. Create shipping via ship-service"]
            B5["5. Clear cart after successful order"]
        end

        subgraph Data["Data Layer"]
            subgraph OrderModel["Order Model"]
                O1["order_id, order_number"]
                O2["customer_id, status"]
                O3["subtotal, shipping_fee"]
                O4["total_amount"]
                O5["payment_id, shipping_id"]
            end
            subgraph OrderItemModel["OrderItem Model"]
                OI1["order_item_id"]
                OI2["order (FK), book_id"]
                OI3["quantity, unit_price"]
                OI4["total_price"]
            end
            DB[(SQLite DB<br/>order.db)]
        end

        API_Layer --> Business
        Business --> Data
        OrderModel --> DB
        OrderItemModel --> DB
    end

    CartSvc["cart-service<br/>(8006)"]
    PaySvc["pay-service<br/>(8008)"]
    ShipSvc["ship-service<br/>(8009)"]

    OrderService -->|"Get cart items"| CartSvc
    OrderService -->|"Create payment"| PaySvc
    OrderService -->|"Create shipping"| ShipSvc
```

### 2.7 Pay Service (Port 8008)

```mermaid
flowchart TB
    subgraph PayService["💳 PAY SERVICE - Port 8008"]
        subgraph API_Layer["API Layer"]
            Payments["/payments/"]
            Process["/process/"]
            Refund["/refund/"]
        end

        subgraph Business["Business Logic"]
            B1["Payment Processing (COD, Card, E-wallet)"]
            B2["Transaction Management"]
            B3["Refund Processing"]
            B4["Payment Status Tracking"]
        end

        subgraph Data["Data Layer"]
            subgraph PaymentModel["Payment Model"]
                P1["payment_id"]
                P2["order_id"]
                P3["amount"]
                P4["method"]
                P5["status"]
            end
            subgraph TransactionModel["Transaction Model"]
                T1["trans_id"]
                T2["payment_id"]
                T3["status"]
                T4["provider"]
            end
            subgraph RefundModel["Refund Model"]
                R1["refund_id"]
                R2["payment"]
                R3["amount"]
                R4["reason"]
            end
            DB[(SQLite DB<br/>pay.db)]
        end

        API_Layer --> Business
        Business --> Data
        PaymentModel --> DB
        TransactionModel --> DB
        RefundModel --> DB
    end

    OrderSvc["order-service<br/>(8007)"]
    OrderSvc -->|"Called by<br/>order creation"| PayService
```

### 2.8 Ship Service (Port 8009)

```mermaid
flowchart TB
    subgraph ShipService["🚚 SHIP SERVICE - Port 8009"]
        subgraph API_Layer["API Layer"]
            Shippings["/shippings/"]
            Track["/track/"]
            CalcFee["/calculate-fee/"]
        end

        subgraph Business["Business Logic"]
            B1["Shipping Rate Calculation"]
            B2["Carrier Selection"]
            B3["Tracking Number Generation"]
            B4["Status Updates"]
            B5["Delivery Estimation"]
        end

        subgraph Data["Data Layer"]
            subgraph ShippingModel["Shipping Model"]
                S1["shipping_id (UUID)"]
                S2["order_id"]
                S3["tracking_number"]
                S4["carrier"]
                S5["status (pending/shipped/delivered)"]
                S6["fee"]
                S7["estimated_delivery"]
            end
            DB[(SQLite DB<br/>ship.db)]
        end

        API_Layer --> Business
        Business --> Data
        ShippingModel --> DB
    end

    OrderSvc["order-service<br/>(8007)"]
    OrderSvc -->|"Called by<br/>order creation"| ShipService
```

### 2.9 Comment-Rate Service (Port 8010)

```mermaid
flowchart TB
    subgraph CommentRateService["⭐ COMMENT-RATE SERVICE - Port 8010"]
        subgraph API_Layer["API Layer"]
            Reviews["/reviews/<br/>GET, POST"]
            Ratings["/ratings/<br/>GET, POST"]
        end

        subgraph Business["Business Logic"]
            B1["Review Submission"]
            B2["Rating Calculation"]
            B3["Update Book Average Rating"]
            B4["Review Moderation"]
        end

        subgraph Data["Data Layer"]
            subgraph ReviewModel["Review Model"]
                RV1["review_id"]
                RV2["book_id"]
                RV3["customer_id"]
                RV4["title, content"]
                RV5["is_verified"]
            end
            subgraph RatingModel["Rating Model"]
                RT1["rating_id"]
                RT2["book_id"]
                RT3["customer_id"]
                RT4["score (1-5)"]
                RT5["created_at"]
            end
            DB[(SQLite DB<br/>comment_rate.db)]
        end

        API_Layer --> Business
        Business --> Data
        ReviewModel --> DB
        RatingModel --> DB
    end

    BookSvc["book-service<br/>(8005)"]
    CommentRateService -->|"Update<br/>average_rating"| BookSvc
```

### 2.10 Recommender AI Service (Port 8011)

```mermaid
flowchart TB
    subgraph RecommenderService["🤖 RECOMMENDER AI SERVICE - Port 8011"]
        subgraph API_Layer["API Layer"]
            Recommend["/recommendations/{customer_id}/"]
            Track["/track-behaviour/"]
        end

        subgraph AI_Engine["AI/ML Engine"]
            subgraph Algorithms["Recommendation Algorithms"]
                A1["Collaborative Filtering"]
                A2["Content-Based Filtering"]
                A3["Hybrid Approach"]
                A4["Popularity-Based"]
            end
            subgraph Analysis["User Behaviour Analysis"]
                AN1["View History"]
                AN2["Purchase History"]
                AN3["Search Patterns"]
                AN4["Rating Patterns"]
            end
        end

        subgraph Data["Data Layer"]
            subgraph BehaviourModel["UserBehaviour Model"]
                UB1["customer_id"]
                UB2["book_id"]
                UB3["action_type"]
                UB4["timestamp"]
            end
            subgraph RecommendModel["Recommendation Model"]
                RC1["recommendation_id"]
                RC2["customer_id"]
                RC3["book_ids"]
                RC4["score"]
            end
            DB[(SQLite DB<br/>recommender.db)]
        end

        API_Layer --> AI_Engine
        AI_Engine --> Data
        BehaviourModel --> DB
        RecommendModel --> DB
    end

    BookSvc["book-service<br/>(8005)"]
    OrderSvc["order-service<br/>(8007)"]
    CommentSvc["comment-rate<br/>(8010)"]

    RecommenderService -->|"Get books<br/>metadata"| BookSvc
    RecommenderService -->|"Get purchase<br/>history"| OrderSvc
    RecommenderService -->|"Get ratings"| CommentSvc
```

### 2.11 API Gateway (Port 8000)

```mermaid
flowchart TB
    subgraph APIGateway["🚪 API GATEWAY - Port 8000"]
        subgraph WebUI["Web UI Layer"]
            Home["Home Page"]
            Books["Books Page"]
            Cart["Cart Page"]
            Checkout["Checkout Page"]
            Login["Login Page"]
            Register["Register Page"]
            Orders["Orders Page"]
            StaffPanel["Staff Panel"]
        end

        subgraph Proxy["API Proxy Layer - Route Mapping"]
            R1["/api/books/ → book-service:8005"]
            R2["/api/cart/ → cart-service:8006"]
            R3["/api/orders/ → order-service:8007"]
            R4["/api/auth/ → customer-service:8001"]
            R5["/api/categories/ → catalog-service:8004"]
            R6["/api/reviews/ → comment-rate:8010"]
            R7["/api/recommend/ → recommender:8011"]
        end

        subgraph Features["Gateway Features"]
            F1["Request/Response Transformation"]
            F2["Authentication Middleware"]
            F3["Health Check Aggregation"]
            F4["Error Handling"]
            F5["CORS Configuration"]
            F6["Static Files Serving"]
        end

        WebUI --> Proxy
        Proxy --> Features
    end

    subgraph Services["Microservices"]
        S8001["8001"]
        S8002["8002"]
        S8004["8004"]
        S8005["8005"]
        S8006["8006"]
        S8007["8007"]
        S8008["8008"]
        S8009["8009"]
        S8010["8010"]
        S8011["8011"]
    end

    APIGateway --> Services
```

---

## 📐 3. Sơ Đồ Luồng Dữ Liệu (Data Flow Diagrams)

### 3.1 Customer Registration Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway as API Gateway<br/>(8000)
    participant Customer as customer-svc<br/>(8001)
    participant Cart as cart-svc<br/>(8006)

    Client->>Gateway: POST /register/
    Gateway->>Customer: POST /customers/
    Customer->>Cart: POST /carts/<br/>{customer_id}
    Cart-->>Customer: 201 Created
    Customer-->>Gateway: 201 Created
    Gateway-->>Client: Success ✅
```

### 3.2 Add to Cart Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway as API Gateway<br/>(8000)
    participant Cart as cart-svc<br/>(8006)
    participant Book as book-svc<br/>(8005)

    Client->>Gateway: POST /api/cart/<br/>{book_id, qty}
    Gateway->>Cart: POST /carts/items/
    Cart->>Book: GET /books/{id}/
    Book-->>Cart: Book details<br/>(price, stock)
    Note over Cart: Validate & Add
    Cart-->>Gateway: 201 Created
    Gateway-->>Client: Success ✅
```

### 3.3 Order Creation Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway as Gateway<br/>(8000)
    participant Order as order-svc<br/>(8007)
    participant Cart as cart-svc<br/>(8006)
    participant Pay as pay-svc<br/>(8008)
    participant Ship as ship-svc<br/>(8009)

    Client->>Gateway: POST /checkout/
    Gateway->>Order: POST /orders/
    Order->>Cart: GET /carts/{customer}/
    Cart-->>Order: Cart items
    Order->>Pay: POST /payments/
    Pay-->>Order: Payment ID
    Order->>Ship: POST /shippings/
    Ship-->>Order: Shipping ID
    Order-->>Gateway: Order Created
    Gateway-->>Client: Success ✅
```

### 3.4 Review & Rating Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway as API Gateway<br/>(8000)
    participant Review as comment-rate<br/>(8010)
    participant Book as book-svc<br/>(8005)

    Client->>Gateway: POST /reviews/<br/>{book_id, rating, content}
    Gateway->>Review: POST /ratings/
    Note over Review: Calculate new<br/>average rating
    Review->>Book: PATCH /books/{id}/<br/>{average_rating}
    Book-->>Review: 200 OK
    Gateway->>Review: POST /reviews/
    Review-->>Gateway: 201 Created
    Gateway-->>Client: Success ✅
```

---

## 📐 4. Deployment Architecture (Docker)

```mermaid
flowchart TB
    subgraph DockerHost["🐳 DOCKER HOST"]
        subgraph Network["Docker Network: bookstore-network"]
            subgraph Row1[""]
                GW["api-gateway<br/>:8000<br/>📦 SQLite"]
                CS["customer-svc<br/>:8001<br/>📦 SQLite"]
                SS["staff-svc<br/>:8002<br/>📦 SQLite"]
                CAS["catalog-svc<br/>:8004<br/>📦 SQLite"]
            end
            subgraph Row2[""]
                BS["book-svc<br/>:8005<br/>📦 SQLite"]
                CRS["cart-svc<br/>:8006<br/>📦 SQLite"]
                OS["order-svc<br/>:8007<br/>📦 SQLite"]
                PS["pay-svc<br/>:8008<br/>📦 SQLite"]
            end
            subgraph Row3[""]
                SHS["ship-svc<br/>:8009<br/>📦 SQLite"]
                CMS["comment-rate<br/>:8010<br/>📦 SQLite"]
                RS["recommender<br/>:8011<br/>📦 SQLite"]
            end
        end
    end

    subgraph PortMapping["Port Mapping"]
        P8000["Host:8000 → api-gateway:8000"]
        P8001["Host:8001 → customer-service:8001"]
        P8002["Host:8002 → staff-service:8002"]
        P8004["Host:8004 → catalog-service:8004"]
        P8005["Host:8005 → book-service:8005"]
        P8006["Host:8006 → cart-service:8006"]
        P8007["Host:8007 → order-service:8007"]
        P8008["Host:8008 → pay-service:8008"]
        P8009["Host:8009 → ship-service:8009"]
        P8010["Host:8010 → comment-rate:8010"]
        P8011["Host:8011 → recommender:8011"]
    end
```

---

## 📐 5. Technology Stack Diagram

```mermaid
flowchart TB
    subgraph Presentation["🎨 PRESENTATION LAYER"]
        HTML["HTML5 Templates"]
        CSS["CSS3 Styling"]
        JS["JavaScript<br/>(Fetch API, DOM)"]
    end

    subgraph Application["⚙️ APPLICATION LAYER"]
        subgraph DRF["Django REST Framework"]
            Views["Views"]
            Serializers["Serializers"]
            URLs["URLs"]
            Models["Models"]
        end
        subgraph Django["Django 4.2.7"]
            ORM["ORM"]
            Admin["Admin"]
            Templates["Templates"]
            Forms["Forms"]
        end
    end

    subgraph DataLayer["💾 DATA LAYER"]
        SQLite["SQLite 3<br/>(Separate database per microservice)"]
    end

    subgraph Infrastructure["🏗️ INFRASTRUCTURE LAYER"]
        subgraph Docker["Docker & Docker Compose"]
            Containers["Containers"]
            Networks["Networks"]
            Volumes["Volumes"]
        end
        Python["Python 3.11"]
    end

    Presentation --> Application
    Application --> DataLayer
    DataLayer --> Infrastructure
```

---

## 📊 6. Service Communication Matrix

```mermaid
flowchart LR
    subgraph Services["Service Communication"]
        Customer["Customer<br/>8001"]
        Staff["Staff<br/>8002"]
        Catalog["Catalog<br/>8004"]
        Book["Book<br/>8005"]
        Cart["Cart<br/>8006"]
        Order["Order<br/>8007"]
        Pay["Pay<br/>8008"]
        Ship["Ship<br/>8009"]
        Review["Review<br/>8010"]
        Recommend["Recommend<br/>8011"]
    end

    Customer -->|"POST"| Cart
    Cart -->|"GET"| Book
    Order -->|"GET"| Cart
    Order -->|"POST"| Pay
    Order -->|"POST"| Ship
    Review -->|"PATCH"| Book
    Recommend -->|"GET"| Book
    Recommend -->|"GET"| Order
    Recommend -->|"GET"| Review
```

### Communication Table

| From \ To | Customer | Staff | Catalog | Book | Cart | Order | Pay | Ship | Review | Recommend |
|-----------|:--------:|:-----:|:-------:|:----:|:----:|:-----:|:---:|:----:|:------:|:---------:|
| **Customer** | - | - | - | - | POST | - | - | - | - | - |
| **Staff** | - | - | - | CRUD | - | GET | - | - | - | - |
| **Catalog** | - | - | - | - | - | - | - | - | - | - |
| **Book** | - | - | GET | - | - | - | - | - | - | - |
| **Cart** | - | - | - | GET | - | - | - | - | - | - |
| **Order** | - | - | - | - | GET | - | POST | POST | - | - |
| **Pay** | - | - | - | - | - | - | - | - | - | - |
| **Ship** | - | - | - | - | - | - | - | - | - | - |
| **Review** | - | - | - | PATCH | - | - | - | - | - | - |
| **Recommend** | - | - | - | GET | - | GET | - | - | GET | - |

---

## 📐 7. Domain-Driven Design Overview

```mermaid
flowchart TB
    subgraph Gateway["🚪 API Gateway"]
        GW["api-gateway<br/>Port: 8000"]
    end

    subgraph UserDomain["👤 User Domain"]
        Customer["customer-service<br/>Port: 8001"]
        Staff["staff-service<br/>Port: 8002"]
    end

    subgraph ProductDomain["📚 Product Domain"]
        Catalog["catalog-service<br/>Port: 8004"]
        Book["book-service<br/>Port: 8005"]
    end

    subgraph OrderDomain["🛒 Order Domain"]
        Cart["cart-service<br/>Port: 8006"]
        Order["order-service<br/>Port: 8007"]
        Pay["pay-service<br/>Port: 8008"]
        Ship["ship-service<br/>Port: 8009"]
    end

    subgraph AnalyticsDomain["📊 Analytics Domain"]
        Comment["comment-rate-service<br/>Port: 8010"]
        Recommend["recommender-ai-service<br/>Port: 8011"]
    end

    GW --> UserDomain
    GW --> ProductDomain
    GW --> OrderDomain
    GW --> AnalyticsDomain

    Catalog -.-> Book
    Customer --> Cart
    Cart --> Book
    Order --> Cart
    Order --> Pay
    Order --> Ship
    Comment --> Book
    Recommend --> Book
    Recommend --> Order
```

---

## 📝 Ghi chú

- ✅ Tất cả services sử dụng **REST API** để giao tiếp
- ✅ Mỗi service có **database riêng** (SQLite) đảm bảo tính độc lập
- ✅ **API Gateway** là điểm truy cập duy nhất cho clients
- ✅ Health check endpoint `/health/` được implement ở mỗi service
- ✅ Sử dụng **Docker Compose** để orchestrate tất cả services
