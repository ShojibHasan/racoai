# Deployment and environment guide

## Environment variables

Copy `.env.example` to `.env` and fill in what you need. In dev, most have safe defaults.

| Variable | Purpose | Default in dev |
|----------|---------|----------------|
| `SECRET_KEY` | Django secret | insecure dev key |
| `DEBUG` | debug mode | `true` |
| `ALLOWED_HOSTS` | comma separated hosts | `*` |
| `DATABASE_URL` | Postgres URL; unset means SQLite | unset (SQLite) |
| `REDIS_URL` | Redis URL; unset means local memory cache | unset (LocMem) |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | seeded admin | `admin@racoai.com` / `admin12345` |
| `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` | Stripe keys | unset |
| `BKASH_BASE_URL` / `BKASH_APP_KEY` / `BKASH_APP_SECRET` / `BKASH_USERNAME` / `BKASH_PASSWORD` | bKash sandbox or live | unset |

Payment endpoints raise a clear error when their keys are missing; the rest of the app runs fine without them.

## Run locally

```bash
source venv/bin/activate
cd backend_racoai
python manage.py migrate
python manage.py seed
python manage.py runserver
```

API is at `http://127.0.0.1:8000/api/`, admin at `/admin/` (`admin@racoai.com` / `admin12345`).

## Run with Docker

```bash
cd backend_racoai
docker compose up --build
```

This starts Postgres, Redis, and the web service. On start the web container migrates, seeds, and runs gunicorn on port 8000. Put any payment keys in `.env`; compose passes them through.

## Expose a local backend with ngrok

Payment providers need to reach your webhooks. With the server running on 8000:

```bash
ngrok http 8000
```

Use the printed HTTPS URL as the webhook target in the Stripe and bKash dashboards, for example `https://<id>.ngrok.app/api/payments/webhook/stripe/`.

## Tests

```bash
python manage.py test
```

Model unit tests plus the recommendation algorithm tests. All should pass.
