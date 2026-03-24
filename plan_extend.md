# Clothes-Service Implementation Plan

## Goal
Extend the bookstore microservices system to support multi-product commerce (books + clothes) with a 2-phase rollout: **Phase 1 (MVP)** adds clothes browsing and admin capabilities without checkout; **Phase 2** unifies cart/order models and enables mixed-product transactions.

Additionally, migrate service databases from SQLite to MySQL with a staged rollout and rollback safety.

## Scope

### Phase 1: Clothes Browse MVP
- **Included**: clothes-service CRUD, gallery proxy at API Gateway, clothes listing/detail pages, admin inventory management, health checks
- **Excluded**: clothes checkout, mixed cart support, mixed order processing, clothes recommendations

### Database Platform Upgrade (Cross-Phase)
- **Included**: MySQL infrastructure, per-service schema migration scripts, dual-environment validation, backup/restore runbook
- **Excluded**: multi-region DB replication, cross-service shared database (keep database-per-service boundary)

### Phase 2: Mixed-Cart/Order (post-Phase-1)
- **Included**: refactored cart/order models with `product_type` discriminator, clothes-in-order checkout flow, payment/shipping for mixed baskets, sales tracking per product type
- **Excluded**: recommender engine (Phase 3, post-data collection)

## Requirements

### Functional Requirements

#### Phase 1
- FR1.1: Clothes service exposes REST CRUD: `GET /clothes/`, `POST /clothes/`, `GET /clothes/{id}/`, `PUT /clothes/{id}/`, `DELETE /clothes/{id}/`
- FR1.2: Clothes filtering/search by category, brand, material, size, color, price range
- FR1.3: Inventory stock visibility for each clothing item (real-time, no checkout reservation yet)
- FR1.4: Admin pages: clothes catalog management, stock management (separate from books dashboard)
- FR1.5: Seed pipeline support for clothing data + dynamic attributes
- FR1.6: Health endpoint `/health/` for clothes-service in gateway aggregate

#### Phase 2
- FR2.1: Cart accepts both book and clothing items; renders mixed basket preview
- FR2.2: Order creation from mixed cart; item records persist with `product_type` field
- FR2.3: Payment processing for multi-product orders (single transaction, split to product services on completion)
- FR2.4: Shipping handles mixed-item baskets with Phase-2 default policy: single shipment per order; split shipment deferred to Phase 3
- FR2.5: Sales sync routes to book-service or clothes-service per item type
- FR2.6: Backward compatibility: existing book-only carts/orders continue to work

#### Database Migration (MySQL)
- FRDB.1: Each service supports MySQL connection via environment-based Django settings
- FRDB.2: Data migration path from SQLite -> MySQL is documented and repeatable per service
- FRDB.3: Zero shared schema across services (database-per-service remains enforced)
- FRDB.4: Rollback path exists to restore SQLite snapshot if MySQL cutover fails
- FRDB.5: Seed scripts and admin flows run correctly on MySQL after cutover

### Non-Functional Requirements
- **Latency**: 
   - P95 `GET /api/clothes/` <= 200ms, P99 <= 350ms at API Gateway
   - Benchmark profile: 10k clothing records, 20 RPS sustained for 5 minutes, warm cache
   - Measured in staging with same Docker topology as production
- **Consistency**: inventory stock updates eventually consistent across cart validation and order fulfillment (timeout retries acceptable)
- **Backward compatibility**: no breaking changes to book-only workflows; cart/order schema migration must be reversible for 2 weeks post-Phase-2 deploy
- **Availability**: clothes-service optional dependency for Phase 1 cart/order (circuit-breaker if unavailable); required for Phase 2 mixed cart validation
- **Database reliability**: MySQL deployment target >= 99.9% uptime with automated restart policy and health checks
- **Database performance**: P95 read query < 80ms on hot paths (catalog list, cart read, order read) under staging benchmark profile

## Architecture Changes

### New Service: clothes-service
**Template**: Django + DRF, follows book-service pattern
- **Models**:
  - `Clothing`: UUID id, name, category, brand, material, price, image_url, stock_quantity, created_at, updated_at
  - `ClothingAttribute`: JSONField for dynamic properties (size, color, fit, care instructions, etc.) per item or variant group
  - Optional: `ClothingVariant` if inventory tracks SKU-level (size+color combinations)
- **API Endpoints**:
  ```
  GET  /clothes/                    # list with filters (category, brand, size, color, price range)
  POST /clothes/                    # create (admin only)
  GET  /clothes/{id}/               # detail
  PUT  /clothes/{id}/               # update (admin only)
  DELETE /clothes/{id}/             # soft delete (admin only)
   GET  /clothes/{id}/stock/         # check inventory availability (cart validation)
   POST /clothes/{id}/stock/         # adjust stock for inventory operations
   POST /clothes/{id}/sales/         # sync total_sold counters after order status transitions
  GET  /health/                     # health check
  ```
- **Docker**: port 8012, environment variables for catalog-service URL (optional dependency)
- **Database**: MySQL (isolated schema/database per service)

### Database Architecture: SQLite -> MySQL
- Keep **database-per-service** model:
   - `book_db`, `catalog_db`, `cart_db`, `order_db`, `customer_db`, `staff_db`, `clothes_db`, etc.
- Each Django service uses MySQL backend config:
   - `ENGINE=django.db.backends.mysql`
   - `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT`
- MySQL deployment options:
   - Option A (simple): one MySQL container with multiple databases/users
   - Option B (strong isolation): one MySQL instance per service group
- Recommendation for this project: start with **Option A** in docker-compose, enforce logical isolation by DB/user permissions.
- Required package updates per service: add `mysqlclient` (or `PyMySQL`) to requirements.

### Catalog-Service Genericization
**Scope**: metadata layer only (non-transactional)
- **New Model**: `DynamicAttribute`
  ```
  product_type: "book" | "clothes"
  category_name: "Fiction", "Sweater", etc.
  attribute_key: "author", "brand", "material"
  attribute_type: "string", "number", "enum", "list"
  required: bool
  enum_values: optional JSON list
  ```
- **Usage**: clothes-service and book-service fetch attribute schema from catalog-service; gateway uses for filter dropdowns
- **Backward compat**: book attributes pre-populated; no changes to book reads until Phase 2

### Cart-Service Refactor (Phase 2)
**Breaking Change - with migration**:
```python
# OLD (Phase 1 state)
class CartItem(models.Model):
    cart_id: UUID
    book_id: UUID          # hardcoded book reference
    quantity: int
    
# NEW (Phase 2)
class CartItem(models.Model):
    cart_id: UUID
    product_id: UUID       # generic product reference
    product_type: Enum["book", "clothes"]
    quantity: int
    snapshot_title: str    # immutable copy at add-time
    snapshot_price: Decimal
    snapshot_image_url: str
```
**Migration**: Use additive migration first (keep `book_id`), backfill to new fields, run compatibility window, then remove legacy field.

**Execution Strategy (safe migration)**:
1. Add new columns (`product_id`, `product_type`, snapshot fields) while keeping `book_id`
2. Backfill `product_id = book_id`, `product_type = "book"`
3. Deploy compatibility layer: accept both `book_id` and `product_id` payloads (dual-read/dual-write)
4. Observe for 2 weeks with rollback window
5. Drop `book_id` only after compatibility window is clean

**Validation Logic** (Phase 2):
```python
def validate_cart_item(product_type, product_id, quantity):
    if product_type == "book":
        call BOOK_SERVICE_URL/books/{id}/stock/
    elif product_type == "clothes":
        call CLOTHES_SERVICE_URL/clothes/{id}/stock/
    else:
        raise ValidationError
```

### Order-Service Refactor (Phase 2)
**Breaking Change - similar migration to cart**:
```python
# OLD (Phase 1)
class OrderItem(models.Model):
    order_id: UUID
    book_id: UUID
    title: str
    price: Decimal
    quantity: int
    
# NEW (Phase 2)
class OrderItem(models.Model):
    order_id: UUID
    product_id: UUID
    product_type: Enum["book", "clothes"]
    title: str
    price: Decimal
    quantity: int
```
**Sales Sync** (Phase 2):
- On order completion, route item to correct service: `POST /books/{id}/sales/` or `POST /clothes/{id}/sales/`
- Track batch status: once all product-specific syncs succeed, mark order as finalized

### API Gateway Updates
**Phase 1**:
- Add clothes-service URL to `settings.py`: `CLOTHES_SERVICE_URL = os.getenv("CLOTHES_SERVICE_URL", "http://clothes-service:8000")`
- Add proxy mapping in `get_service_url()`: `"clothes": CLOTHES_SERVICE_URL`
- Add routes in gateway URLs: `/api/clothes/`, `/clothes/` (browse pages)
- Add templates: `clothes.html` (listing), `clothes_detail.html`, `clothes_inventory.html` (admin)

**Phase 2**:
- Update cart/order proxy to handle mixed-product payloads
- Aggregate health check to include clothes-service

### Docker-Compose
**Phase 1 Addition**:
```yaml
mysql:
   image: mysql:8.0
   restart: unless-stopped
   environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-rootpass}
   ports:
      - "3306:3306"
   volumes:
      - mysql_data:/var/lib/mysql
      - ./docker/mysql/init:/docker-entrypoint-initdb.d
   healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 10
   networks:
      - bookstore-network

clothes-service:
  build: ./clothes-service
  ports:
    - "8012:8000"
  environment:
    - DEBUG=1
    - CATALOG_SERVICE_URL=http://catalog-service:8000
      - DB_ENGINE=mysql
      - DB_NAME=clothes_db
      - DB_USER=clothes_user
      - DB_PASSWORD=clothes_pass
      - DB_HOST=mysql
      - DB_PORT=3306
  depends_on:
      - catalog-service
         - mysql
  networks:
    - bookstore-network
  
# api-gateway additions:
environment:
   - CLOTHES_SERVICE_URL=http://clothes-service:8000
    - DB_ENGINE=mysql
    - DB_HOST=mysql
    - DB_PORT=3306
depends_on:
  - clothes-service
   - mysql

volumes:
   mysql_data:
```

## Phase Plan

### Phase 0: Database Migration Foundation (SQLite -> MySQL)
**Duration**: 1-2 weeks | **Dependency Chain**: Infra -> Config -> Schema -> Data Copy -> Validation -> Cutover

1. **MySQL Infrastructure Setup** (Days 1-2)
   - Add MySQL service to docker-compose with persistent volume and healthcheck
   - Create init SQL scripts for per-service databases and users
   - Add backup script for SQLite snapshots before cutover

2. **Service Configuration Upgrade** (Days 3-4)
   - Update each service settings.py to support DB selection by env (`sqlite` or `mysql`)
   - Add MySQL driver dependency (`mysqlclient` preferred)
   - Keep SQLite as fallback during transition window

3. **Schema + Data Migration Rehearsal** (Days 5-6)
   - Run Django migrations against MySQL for each service
   - Export/import seed and existing dev data from SQLite to MySQL
   - Validate row counts and critical entities parity

4. **Cutover + Verification** (Days 7-9)
   - Switch compose env to MySQL for all services in staging
   - Run smoke tests for auth/catalog/book/cart/order flows
   - Execute rollback drill (restore SQLite) and document RTO

5. **Go/No-Go for Feature Phases** (Day 10)
   - Proceed to Clothes Phase 1 only after MySQL baseline is stable

---

### Phase 1: Clothes Service MVP (Browse + Admin, No Checkout)
**Duration**: 3-4 weeks | **Dependency Chain**: Req -> Service -> Docker -> Gateway -> Frontend -> Seed -> Test

1. **Requirements Finalization** (Day 1)
   - Finalize clothing attributes (size range, color palette, brands, materials)
   - Finalize inventory rules (stock tracking: per-item or per-variant? reorder thresholds?)
   - Decide: start with simpler per-item model; variants in Phase 2 if needed

2. **Clothes-Service Implementation** (Days 2–8)
   - Scaffold Django service from book-service template
   - Define `Clothing`, `ClothingAttribute` models
   - Implement serializers, viewsets, URL routing
   - Add `/health/` endpoint
   - Add admin panel for staff bulk upload

3. **Docker Integration** (Day 9)
   - Write Dockerfile, entrypoint.sh, requirements.txt
   - Wire docker-compose.yml with port 8012, env vars, network config
   - Verify service boots, health endpoint responds

4. **Gateway Proxy** (Days 10–11)
   - Register CLOTHES_SERVICE_URL in settings.py
   - Add proxy routes: `/api/clothes/`, `/api/clothes/{id}/`
   - Add service URL mapping function

5. **Frontend: Clothes Pages** (Days 12–14)
   - Create `clothes.html` (listing with filters: category, brand, size, color, price)
   - Create `clothes_detail.html` (detail, out-of-stock messaging)
   - Create `clothes_inventory.html` (admin stock management page)
   - Add navigation menu item linking to clothes catalog

6. **Seed Pipeline** (Days 15–16)
   - Extend `seed_data.py` with clothes seeding function
   - Load sample clothing data (5–10 items per category) for testing
   - Load dynamic attributes into catalog-service

7. **Phase 1 Verification** (Days 17–20)
   - Smoke test: POST /clothes/, GET /clothes/, GET /clothes/{id}/, PUT, DELETE
   - Health check: docker-compose up, services healthy
   - List/filter: test search filters return correct results
   - Seed idempotency: run seed twice, no duplicates
   - UI: manual browse clothes pages in browser

**Go/No-Go Gate**: Health ✓, API contract ✓, UI ✓, backward compat book flow ✓ → **Proceed to Phase 2**

---

### Phase 2: Mixed Cart + Order Refactor (Checkout Enabled)
**Duration**: 4–5 weeks | **Dependency Chain**: Cart schema → Order schema → Service integration → Validation → Frontend → E2E testing

1. **Catalog-Service Genericization** (Days 1–3)
   - Design `DynamicAttribute` model in catalog-service
   - Pre-populate book attributes (author, publisher, category, format)
   - Pre-populate clothes attributes (brand, material, size, color, fit)
   - Expose attribute schema via new endpoint: `GET /attributes/?product_type=book|clothes`

2. **Cart-Service Schema Migration** (Days 4–7)
   - Add columns: `product_id`, `product_type` (default "book") while keeping `book_id`
   - Add snapshot fields: `snapshot_title`, `snapshot_price`, `snapshot_image_url`
   - Write data migration: backfill `product_id=book_id`, `product_type="book"` where `book_id not null`
   - Update serializers to accept both `book_id` (legacy) and `product_id` + `product_type` (new)
   - Keep dual-read/dual-write for 2-week compatibility window, then remove `book_id`

3. **Cart Service Validation Routing** (Days 8–10)
   - Refactor `AddCartItem` view to branch on `product_type`
   - Implement HTTP calls: check book-service or clothes-service stock endpoint
   - Add circuit-breaker: if clothes-service unavailable, reject clothes items (fail-safe in Phase 1 transition)
   - Test mixed cart (1 book + 1 clothing item) added successfully

4. **Order-Service Schema Migration** (Days 11–14)
   - Add columns: `product_id`, `product_type` (default "book") while keeping `book_id`
   - Update `CreateOrder` to accept mixed cart items
   - Implement sales sync dispatcher: for each OrderItem, call `POST /books/{id}/sales/` or `POST /clothes/{id}/sales/`
   - Handle partial sync failure: retry with backoff, eventual consistency

5. **Payment & Shipping Integration (Phase 2 Scope)** (Days 15–18)
   - Payment: create single transaction for mixed cart, charge total amount
   - On payment success: dispatch sales updates to book-service and clothes-service in parallel
   - Shipping (fixed policy for Phase 2): single shipment per order with one shipping fee and one tracking code; split shipment is explicitly deferred to Phase 3
   - Update order status flow: pending → paid → shipped (unified, no per-product sequencing)

6. **Gateway Templates & API** (Days 19–21)
   - Update `cart.html`: render mixed items (book and clothes thumbnails, sizes/variants)
   - Update `checkout.html`: show mixed summary, single payment form
   - Update `orders.html`: display items with product_type icon (book icon vs. shirt icon)
   - Add API endpoint to support product_type filtering in orders list

7. **Phase 2 Verification** (Days 22–25)
   - E2E test: add book → add clothing → checkout → payment success → order created with both items
   - Sales sync: verify counters increment in both book-service and clothes-service
   - Refund/cancel: subtract from both services correctly
   - Backward compat: book-only cart/order flow unchanged (no regressions)
   - Stress: concurrent mixed orders (5+ carts with 10+ items each)

**Go/No-Go Gate**: E2E ✓, sales sync ✓, refund ✓, performance ✓, backward compat ✓ → **Phase 2 Complete, Announce New Feature**

---

### Phase 3: Recommendations & Analytics (Post-Data Collection)
**Deferred**: Implement after ~1000 clothing orders collected (3–6 months post-Phase-2)
- Extend `recommender-ai-service` behavior schema with `product_type`
- Build candidate generation for clothing (trending, user-preference matching)
- Update staff/manager dashboards to show product-type breakdowns

## Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Phase 2 cart/order schema migration breaks existing book orders | High | Write data migration with backfill; test on staging with real data backup; rollback script prepared; 2-week grace period to revert |
| Mixed-cart payment splits incorrectly or loses items | High | Unit test payment dispatcher per item type; E2E test 100+ mixed orders before release; add idempotency keys to prevent double-charges |
| Clothes-service unavailable → Phase 2 mixed carts fail | Medium | Circuit-breaker: reject clothes items if service unreachable; document fallback (book-only checkout); alert on clothes-service health |
| Catalog-service attribute schema too rigid for edge cases | Medium | Start with JSONField (flexible); add validation layer; track attribute schema versions per product_type |
| Sales sync lag → inventory counts diverge between services | Medium | API retries with exponential backoff; periodic reconciliation job; accept ±2% variance as acceptable eventual consistency |
| Performance: gateway adds latency for mixed cart validation | Low | Parallelize service calls (validate book + clothes in parallel); cache attribute schema; target P99 <= 350ms (staging profile) |
| Staff/manager dashboards break after Phase 2 schema change | Medium | Update dashboard queries to filter by product_type="book" for existing KPIs; add new product-type breakdowns in Phase 3 |
| MySQL cutover causes service startup/migration failures | High | Stage-first cutover, preflight migrations per service, keep SQLite fallback and rollback scripts |
| Data mismatch between SQLite and MySQL after migration | High | Row-count parity checks + checksum sampling on critical tables before go-live |
| Connection pool saturation on MySQL under mixed-cart load | Medium | Configure Django DB CONN_MAX_AGE and MySQL max_connections; load-test before production cutover |

## Verification Checklist

### Database Migration Completion Criteria
- [ ] MySQL container healthy and persistent volume mounted
- [ ] Per-service databases/users created with least privilege
- [ ] All services can run migrations against MySQL successfully
- [ ] Data parity verified (row counts + sampled records) after SQLite -> MySQL copy
- [ ] Full staging smoke test passes with MySQL-only mode
- [ ] Rollback drill to SQLite completed and documented
- [ ] Backup/restore scripts validated

### Phase 1 Completion Criteria
- [ ] Clothes-service `/health/` responds 200
- [ ] CRUD operations (POST, GET, PUT, DELETE) work via gateway and direct service
- [ ] Clothes listing filters work (category, brand, size, color, price)
- [ ] Seed pipeline runs without duplicates
- [ ] Clothes detail page renders correctly in browser
- [ ] Inventory stock is visible to admins
- [ ] Book-only cart/orders still work (no regression)
- [ ] Gateway health aggregate includes clothes-service status
- [ ] RBAC enforced: unauthenticated requests denied for admin-only clothes endpoints
- [ ] RBAC enforced: non-manager/non-admin cannot access clothes admin pages

### Phase 2 Completion Criteria
- [ ] Cart accepts `product_type` field in add-item payload
- [ ] Mixed cart (1 book + 1 clothes) checkout succeeds
- [ ] Order created with both book and clothing items
- [ ] Payment charged once for total amount
- [ ] Sales sync called for both book-service and clothes-service
- [ ] Book inventory counter increments on book order
- [ ] Clothes inventory counter increments on clothing order
- [ ] Refund flow decrements both counters correctly
- [ ] Order cancellation updates both product services
- [ ] Backward compat: book-only cart/order still work
- [ ] Backward compat window active: legacy `book_id` payload still accepted during transition
- [ ] Gateway response time for mixed cart <= 350ms P99 (staging benchmark profile)
- [ ] Staff dashboards show books KPIs (no clothes mixed in)
- [ ] Mobile UI renders mixed cart correctly

### Regression Testing
- [ ] Book search, filtering, purchase unchanged
- [ ] Customer order history displays correctly
- [ ] Staff inventory management pages work
- [ ] Payment flow for books unaffected
- [ ] Shipping labels print correctly for mixed orders

## Deliverables

### Code & Configuration
1. **clothes-service/** directory
   - `Dockerfile`, `entrypoint.sh`, `requirements.txt`, `manage.py`
   - `clothes_service/settings.py`
   - `app/models.py` (Clothing, ClothingAttribute)
   - `app/serializers.py` (ClothingSerializer)
   - `app/views.py` (ClothingViewSet, health endpoint)
   - `app/urls.py` (routing)
   - `app/admin.py` (Django admin)

2. **api-gateway/** updates
   - `api_gateway/settings.py` (CLOTHES_SERVICE_URL)
   - `app/views.py` (proxy routing, get_service_url() update)
   - `app/urls.py` (clothes routes)
   - `templates/clothes.html`, `clothes_detail.html`, `clothes_inventory.html`
   - `templates/cart.html` (mixed item rendering)
   - `templates/checkout.html` (mixed summary)
   - `templates/orders.html` (mixed items with icons)

3. **Data & Seed**
   - `seed_data.py` (clothes seeding function)
   - Sample clothing data CSV or JSON (5–10 items per category)

4. **Database Migrations**
   - `cart-service`: migrations for schema change (product_type, product_id rename)
   - `order-service`: migrations for schema change
   - `catalog-service`: DynamicAttribute model creation
   - DB platform migration scripts/runbook: SQLite -> MySQL per service

5. **docker-compose.yml**
   - mysql service definition (volume, healthcheck, init scripts)
   - clothes-service definition with port 8012, env vars, depends_on
   - api-gateway env var additions for CLOTHES_SERVICE_URL
   - DB env vars for all services (`DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`)

### Documentation
1. **Implementation Guide** (how to run Phase 1 and Phase 2)
2. **API Documentation Addendum** (clothes endpoints, mixed cart payload examples)
3. **Schema Migration Guide** (backup/restore procedures, rollback instructions)
4. **Troubleshooting** (common circuit-breaker scenarios, sales sync failures, MySQL connection issues)
5. **DB Cutover Guide** (SQLite export/import, parity check, rollback decision matrix)

### Testing Artifacts
1. **Unit Tests**: clothes-service CRUD, cart validation logic per product_type
2. **Integration Tests**: gateway proxy, service-to-service calls
3. **E2E Tests**: mixed-product checkout flow, refund, cancellation
4. **Seed Verification**: idempotency, no duplicate attributes

### Deployment Checklist
1. Feature flag toggle (optional): enable *mixed cart* only after Phase 2 validation
2. Health check dashboard: clothes-service and all integrations
3. Rollback playbook: if Phase 2 causes outages, restore Phase 1 state
4. Communication: announce Phase 1 launch (clothes browsing); Phase 2 launch (checkout)
5. Database cutover approval: DBA/owner sign-off before enabling MySQL-only mode
