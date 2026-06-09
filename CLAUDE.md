# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and Python 3.12+.

```bash
# Run the development server
uv run python manage.py runserver

# Apply migrations
uv run python manage.py migrate

# Create a new migration after model changes
uv run python manage.py makemigrations

# Run tests
uv run python manage.py test

# Run a single test module
uv run python manage.py test store

# Open the Django shell
uv run python manage.py shell

# Create a superuser for the admin panel
uv run python manage.py createsuperuser
```

## Architecture

This is a Django 6 e-commerce app with a single `store` app and a `demoProject` settings package.

### Cart design

The cart is **session-backed but DB-persisted**. `store/cart.py::SessionCart` wraps a `Cart` model row keyed by `request.session.session_key`. Every mutation (add/remove/update/clear) hits the database directly — there is no in-memory or cookie-only cart state. The session key is the join between the anonymous browser session and the `Cart` row.

`store/context_processors.py::cart_summary` injects `cart_item_count` and `cart_total` into every template request, powering the header badge without extra view logic.

### Order flow

Checkout (`views.checkout`) performs stock validation inline before creating the `Order`, then decrements `Product.stock` for each `OrderItem` created. `OrderItem` snapshots `product_name` and `product_price` at order time so order history is stable even if the `Product` record changes later.

### URL namespacing

All store URLs use the `store:` namespace (e.g. `{% url 'store:cart' %}`). Auth URLs (`/accounts/login/`, etc.) come from `django.contrib.auth.urls`.

### Templates

Global templates live in `templates/` (base layout, login, register). Store-specific templates live in `templates/store/`. All extend `base.html`. Global static CSS is at `static/css/store.css`.
