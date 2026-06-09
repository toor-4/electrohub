# Django E-Commerce Store

A Django 6 e-commerce application with product browsing, a session-backed cart, and order checkout.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

## Setup

```bash
# Install dependencies
uv sync

# Apply database migrations
uv run python manage.py migrate

# (Optional) Seed sample data
uv run python manage.py seed_data

# Create an admin superuser
uv run python manage.py createsuperuser

# Start the development server
uv run python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Features

- **Product catalog** — categories, brands, stock tracking, featured products
- **Shopping cart** — session-backed, DB-persisted cart (no cookie state)
- **Checkout** — inline stock validation, order creation with shipping details
- **Order history** — price/name snapshots so history is stable after product edits
- **Admin panel** — full Django admin at `/admin/`
- **Auth** — registration, login, logout via `django.contrib.auth`

## Project Structure

```
demoProject/   # Django settings, root URLconf
store/         # Main app: models, views, cart, forms, URLs
templates/     # Base layout + store-specific templates
static/        # Global CSS
```

## Testing

```bash
uv run python manage.py test store
```
