# RacoAI E-commerce Backend

A REST API for an e-commerce ordering and payment system. It manages users, products, orders, and payments, with two payment providers (Stripe and bKash) behind a strategy pattern. Built with Django, Django REST Framework, and JWT auth.

## Features

- Email-login users with JWT (register, login, refresh, me).
- Products with admin CRUD and a self-referential category tree.
- Orders with server-computed subtotals and totals.
- Payments via Stripe and bKash, with webhooks and atomic stock reduction after a successful payment.
- Product recommendations using DFS over the category tree, cached in Redis.
- UUID primary keys, seed data, Docker, and OpenAPI/Swagger docs.

## Requirements

- Python 3.12
- Redis and PostgreSQL are optional locally (SQLite and in-memory cache are used by default).

## Run locally

```bash
# from the repo root
source venv/bin/activate
cd backend_racoai
pip install -r requirements.txt

cp .env.example .env   # adjust values as needed

python manage.py migrate
python manage.py seed          # admin user + sample products
python manage.py runserver
```

The API is at `http://127.0.0.1:8000/api/`. Admin is at `/admin/` (default seeded login `admin@racoai.com` / `admin12345`).

## API docs

- Swagger UI: `http://127.0.0.1:8000/api/docs/`
- ReDoc: `http://127.0.0.1:8000/api/redoc/`
- OpenAPI spec: `http://127.0.0.1:8000/api/schema/`
- Written reference: `docs/api/api-documentations.md`

## Run with Docker

```bash
docker compose up --build
```

This starts the web service with PostgreSQL and Redis. On start it migrates, seeds, and serves via gunicorn on port 8000.

## Tests

```bash
python manage.py test
```

## More docs

See `docs/`: architecture diagram, ERD, payment flow diagrams, and the deployment and environment guide.
