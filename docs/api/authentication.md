# Authentication API

Base path: `/api/auth/`. Auth uses JWT (SimpleJWT). Send the access token as `Authorization: Bearer <token>` on protected endpoints.

## Register

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

## Login

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

## Refresh

`POST /api/auth/refresh/` (open)

Request:

```json
{ "refresh": "<jwt>" }
```

Response `200`:

```json
{ "access": "<jwt>" }
```

## Current user

`GET /api/auth/me/` (requires auth)

Response `200`:

```json
{ "id": 1, "email": "user@example.com", "full_name": "Jane Doe", "date_joined": "2026-07-22T15:16:32Z" }
```
