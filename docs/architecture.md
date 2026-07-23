# System architecture

The backend is a Django REST Framework API split into domain apps. Clients talk to the API over HTTP with JWT. Payments go through external providers behind a strategy pattern. Postgres is the store of record; Redis caches the category tree.

```mermaid
flowchart TB
    client["Client (web / mobile / Postman)"]
    ext_stripe["Stripe"]
    ext_bkash["bKash"]

    subgraph api["Django REST Framework API"]
        auth["accounts (JWT auth)"]
        catalog["catalog (products, categories)"]
        orders["orders (orders, items, totals)"]
        payments["payments (strategy providers)"]
        recs["recommendations (DFS)"]
    end

    db[("PostgreSQL")]
    redis[("Redis (category tree cache)")]

    client -->|"HTTPS + Bearer JWT"| api
    auth --> db
    catalog --> db
    orders --> db
    payments --> db
    recs --> db
    recs --> redis

    payments -->|initiate / verify| ext_stripe
    payments -->|initiate / verify| ext_bkash
    ext_stripe -->|webhook| payments
    ext_bkash -->|callback| payments
```

## Notes

- Each app owns one domain. Payment providers plug in through a registry, so order logic never changes when a provider is added.
- Stock is reduced only after a verified successful payment, inside an atomic transaction with row locking.
- The category tree is cached in Redis and invalidated by a signal on category change.
