# Project report: RacoAI e-commerce backend

A REST API for an e-commerce ordering and payment system: users, products, orders, and payments across two providers (Stripe and bKash). Built with Python 3.12, Django 5.1, and Django REST Framework.

## 1. Implementation approach and rationale

The system is split into domain apps, each owning one responsibility: `accounts` (users and auth), `catalog` (products and categories), `orders` (orders and line items), `payments` (providers and settlement), and `recommendations` (DFS over the category tree). Keeping domains separate makes each part easy to reason about and lets features grow without one module swelling.

Key decisions and why:

- **Custom user model with email login.** The requirement is a unique email used to log in. `AbstractBaseUser` plus `PermissionsMixin` with a custom `UserManager` gives full control over the fields and drops the username entirely. Set at the start of the project because swapping the user model later is painful.
- **JWT auth (SimpleJWT).** Stateless tokens mean no server-side session lookup per request, which scales cleanly. Short access token (30 min) limits the blast radius of a leaked token; a longer refresh token (1 day) keeps users logged in.
- **Server-computed order totals.** The client sends only product ids and quantities. Prices, subtotals, and the order total are computed on the server from the product, so totals cannot be tampered with. Subtotal is derived in `OrderItem.save()` and the total in `Order.recalculate_total()`, making the math deterministic and centralized.
- **Strategy pattern for payments.** A `PaymentProvider` abstract base defines `initiate()` and `verify()`; `StripeProvider` and `BkashProvider` implement them; a registry resolves a provider by name. Adding a provider is one class plus one registry entry, with no change to order logic, which is exactly what the requirement asks for.
- **Stock reduced only after a verified success, atomically.** Settlement runs in `transaction.atomic`, locks the payment row with `select_for_update` (so repeated webhooks settle once), and locks and re-checks each product row before reducing stock (so concurrent payments cannot oversell). Failure or insufficient stock cancels the order and leaves stock untouched.
- **DFS recommendations with Redis cache.** The category tree is built once into an adjacency map and cached. An iterative (stack-based) DFS walks the product's category branch to find related products. A signal on category change invalidates the cache; a TTL is a safety net.
- **UUID primary keys.** A shared abstract `UUIDModel` gives every model a `uuid4` id, so ids do not leak row counts and are safe across systems.
- **Config from environment.** Database, cache, secret key, and provider keys all come from environment variables, so the same image runs on SQLite locally and PostgreSQL in Docker with no code change.

## 2. Rejected alternatives

| Decision | Chosen | Rejected | Why |
|----------|--------|----------|-----|
| Framework | Django + DRF | FastAPI, Flask | Django ships ORM, migrations, admin, and auth, cutting boilerplate for a data-heavy app. FastAPI would need those bolted on. |
| User model | `AbstractBaseUser` + email | Default `User`, `AbstractUser` | Requirement is email-only login with no username; the default carries a username field. |
| Payment integration | Strategy pattern + registry | if/else on provider name in order code | Requirement demands adding providers without touching order logic; branching would spread provider knowledge across the codebase. |
| Stock reduction timing | After verified payment | At order creation | Reserving stock for unpaid orders starves real buyers; the flow specifies reduction after success. |
| Overselling guard | `select_for_update` + re-check | Optimistic check before save | Two concurrent payments could both pass a naive check and drive stock negative; row locks serialize them. |
| Money field | `DecimalField` | `FloatField` | Floats cannot represent money exactly, causing rounding errors in totals. |
| Category cache | Redis (Django cache) | Custom in-process cache, no cache | Redis is shared across workers and standard; a custom cache is unneeded work; no cache re-queries the tree on every recommendation. |
| Primary key | UUID | Auto-increment integer | Sequential ids leak counts and collide across systems; the change was requested. |
| UUID migration | Regenerate initial migrations | In-place PK-altering data migration | No production data exists, so a clean regenerate is simpler and safer than a fragile alter-and-backfill. |
| DFS style | Iterative (explicit stack) | Recursive | A deep category tree could exceed Python's recursion limit; a stack avoids that. |
| API docs | drf-spectacular (Swagger) | Hand-written only | Generated docs stay in sync with the code; hand-written docs drift. Both are kept, generated for accuracy and markdown for quick reading. |

## 3. Testing approach and reports

Tests are scoped to models and the one required algorithm (DFS), per the agreed scope. Each app's models are covered with focused unit tests; the recommendations app has no model, so its tests cover the DFS and recommendation logic instead.

What is covered:

- **accounts:** create user, create superuser, email required, email normalized, email unique, password not stored raw (6 tests).
- **catalog:** product defaults, str, sku unique; category parent relation, slug unique, str (6 tests).
- **orders:** order defaults, subtotal auto-computed, total recalculated, str (4 tests).
- **payments:** payment defaults, transaction_id unique, str, is_settled (4 tests).
- **recommendations:** DFS descendants, leaf returns self, recommendation covers the branch and excludes self, inactive skipped, no category returns empty (5 tests).

Beyond unit tests, each feature was checked end to end with a manual smoke test at build time: register and login flow, admin-only product writes, order creation with server-side totals, the full payment settle path with a fake provider (success reduces stock, duplicate webhook is idempotent, failure and oversell cancel and leave stock intact), category-tree caching (1 query then 0 on a cache hit), and UUIDs flowing through the API.

Latest report:

```
Ran 25 tests ... OK
System check identified no issues (0 silenced).
spectacular schema build: 0 errors, 0 warnings
```

Not covered by automated tests, by scope choice: API-level and webhook integration tests. The manual smoke tests exercise those paths, but they are not committed as a suite. This is a known, deliberate gap.

## 4. API and router documentation

All endpoints live under `/api/`. Routing is wired by including each app's `urls` into `config/urls.py`. CRUD resources use DRF `DefaultRouter`, which generates the list and detail routes from a viewset; simpler endpoints use explicit `path()` entries.

| Area | Base path | Auth | Notes |
|------|-----------|------|-------|
| Auth | `/api/auth/` | open (login/register) | register, login, refresh, me |
| Products | `/api/products/` | read open, write staff | filter by status and category |
| Categories | `/api/categories/` | read open, write staff | list returns the tree |
| Orders | `/api/orders/` | authenticated | create, list own, retrieve own |
| Payments | `/api/payments/` | authenticated + open webhooks | initiate, stripe/bkash webhooks, list own |
| Recommendations | `/api/recommendations/{id}/` | open | DFS related products |

Routing specifics:

- Viewsets (`ProductViewSet`, `CategoryViewSet`, `OrderViewSet`, `PaymentViewSet`) register on `DefaultRouter` instances, one per app, and the router urls are included under `/api/`.
- The payment webhooks and the recommendation endpoint are plain `APIView`s wired with explicit `path()` because they do not map to standard CRUD.
- Permissions are enforced per view: a custom `IsAdminOrReadOnly` for catalog, per-user querysets for orders and payments, and `AllowAny` on webhooks and docs.

Live and written docs:

- Swagger UI at `/api/docs/`, ReDoc at `/api/redoc/`, OpenAPI spec at `/api/schema/` (drf-spectacular).
- Written reference at `docs/api/api-documentations.md`.
- Diagrams at `docs/architecture.md`, `docs/erd.md`, `docs/payment-flows.md`.

## 5. Final verdict

Every functional and design requirement is implemented and verified: user management, product management with categories, orders with deterministic totals, payments across Stripe and bKash behind a strategy pattern, safe post-payment stock reduction, DFS recommendations with Redis caching, migrations, environment-based secrets, seed data, Docker, Swagger docs, and logging. All 25 tests pass and the schema builds clean.

Two items are deliberately out of the delivered scope: automated API and webhook integration tests (covered manually, not committed as a suite), and live-mode provider credentials (supplied by the operator via environment variables). Neither blocks running or reviewing the system.

The backend is complete, runs locally and in Docker, and is ready for review.
