# Entity relationship diagram

Core entities and their relationships. A user places orders; an order holds order items; each item points at a product; a product may belong to a category tree; an order is paid through one or more payment attempts.

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ ORDERITEM : contains
    PRODUCT ||--o{ ORDERITEM : "ordered as"
    CATEGORY ||--o{ PRODUCT : groups
    CATEGORY ||--o{ CATEGORY : "parent of"
    ORDER ||--o{ PAYMENT : "paid by"

    USER {
        bigint id PK
        string email UK
        string full_name
        bool is_staff
        bool is_active
        datetime date_joined
    }
    CATEGORY {
        bigint id PK
        string name
        string slug UK
        bigint parent_id FK
    }
    PRODUCT {
        bigint id PK
        string name
        string sku UK
        text description
        decimal price
        int stock
        string status
        bigint category_id FK
        datetime created_at
        datetime updated_at
    }
    ORDER {
        bigint id PK
        bigint user_id FK
        decimal total_amount
        string status
        datetime created_at
        datetime updated_at
    }
    ORDERITEM {
        bigint id PK
        bigint order_id FK
        bigint product_id FK
        int quantity
        decimal price
        decimal subtotal
    }
    PAYMENT {
        bigint id PK
        bigint order_id FK
        string provider
        string transaction_id UK
        string status
        json raw_response
        datetime created_at
        datetime updated_at
    }
```

## Relationship notes

- USER to ORDER: one user has many orders.
- ORDER to ORDERITEM: one order has one or more items (cascade delete).
- PRODUCT to ORDERITEM: protected, a product referenced by an order cannot be deleted.
- CATEGORY to PRODUCT: a product may have one category or none (set null on delete).
- CATEGORY to CATEGORY: self referential tree via parent (cascade delete to children).
- ORDER to PAYMENT: an order can have several payment attempts; transaction id is unique.
