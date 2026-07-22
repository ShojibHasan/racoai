# API documentation

Single reference for all RacoAI backend endpoints. One section per feature area, updated as each feature lands.

Auth uses JWT (SimpleJWT). Send the access token as `Authorization: Bearer <token>` on protected endpoints.

## Sections

- [Authentication](#authentication) (`/api/auth/`)
- [Products](#products) (`/api/products/`)
- [Categories](#categories) (`/api/categories/`)

---

## Authentication

Base path: `/api/auth/`.

### Register

`POST /api/auth/register/` (open)

Request:

```json
{ "email": "user@example.com", "full_name": "Jane Doe", "password": "secretpass" }
```

Response `201`:

```json
{ "id": 1, "email": "user@example.com", "full_name": "Jane Doe" }
```

Errors: `400` if email is taken or password is under 8 characters.

### Login

`POST /api/auth/login/` (open)

Request:

```json
{ "email": "user@example.com", "password": "secretpass" }
```

Response `200`:

```json
{ "access": "<jwt>", "refresh": "<jwt>" }
```

Access token lives 30 minutes, refresh token 1 day.

### Refresh

`POST /api/auth/refresh/` (open)

Request:

```json
{ "refresh": "<jwt>" }
```

Response `200`:

```json
{ "access": "<jwt>" }
```

### Current user

`GET /api/auth/me/` (requires auth)

Response `200`:

```json
{ "id": 1, "email": "user@example.com", "full_name": "Jane Doe", "date_joined": "2026-07-22T15:16:32Z" }
```

---

## Products

Base path: `/api/products/`. Read is open to everyone. Create, update, and delete require a staff user.

### List

`GET /api/products/` (open)

Optional filters: `?status=active|inactive`, `?category=<id>`.

Response `200`: array of product objects.

### Detail

`GET /api/products/{id}/` (open)

```json
{
  "id": 1, "name": "Mug", "sku": "MUG-1", "description": "",
  "price": "9.99", "stock": 0, "status": "active", "category": null,
  "created_at": "2026-07-22T00:00:00Z", "updated_at": "2026-07-22T00:00:00Z"
}
```

### Create

`POST /api/products/` (staff only)

```json
{ "name": "Mug", "sku": "MUG-1", "price": "9.99", "stock": 10, "category": 2 }
```

Response `201` with the created product. `400` on duplicate `sku`. `403` for non-staff, `401` for anonymous.

### Update / Delete

`PUT/PATCH /api/products/{id}/` and `DELETE /api/products/{id}/` (staff only).

## Categories

Base path: `/api/categories/`. Read is open, writes require staff. A category can have a `parent`, forming a tree.

### List

`GET /api/categories/` (open)

Returns root categories with children nested recursively.

```json
[
  { "id": 1, "name": "Electronics", "slug": "electronics", "parent": null,
    "children": [
      { "id": 2, "name": "Phones", "slug": "phones", "parent": 1, "children": [] }
    ]
  }
]
```

### Create

`POST /api/categories/` (staff only)

```json
{ "name": "Phones", "slug": "phones", "parent": 1 }
```

`parent` is optional; omit it for a root category. Response `201`.

### Update / Delete

`PUT/PATCH /api/categories/{id}/` and `DELETE /api/categories/{id}/` (staff only). Deleting a category cascades to its children.
