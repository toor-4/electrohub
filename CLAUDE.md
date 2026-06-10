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

# Open the Django shell
uv run python manage.py shell

# Create a superuser for the admin panel
uv run python manage.py createsuperuser
```

## Testing

### Unit tests & pytest

```bash
# Run all tests
uv run pytest

# Run all tests verbose
uv run pytest -v

# Run a single test file
uv run pytest store/tests.py

# Run a single test by name
uv run pytest store/tests.py::test_checkout_post_creates_order

# Run tests matching a keyword
uv run pytest -k "cart"

# Stop on first failure
uv run pytest -x

# Run with coverage report
uv run pytest --cov=store --cov-report=term-missing
```

Test files follow the `tests.py` / `test_*.py` naming convention (configured in `pyproject.toml`). Django settings are auto-loaded via `DJANGO_SETTINGS_MODULE = "demoProject.settings"` — no extra setup needed.

### Playwright (browser / end-to-end)

```bash
# Install browser binaries (one-time, or after updating playwright)
uv run playwright install chromium

# Install all supported browsers
uv run playwright install

# Run a Playwright script
uv run python tests/e2e/test_home.py

# Run Playwright tests via pytest-playwright (if installed)
uv run pytest tests/e2e/ --headed          # show the browser window
uv run pytest tests/e2e/ --slowmo=500      # slow down interactions (ms)
uv run pytest tests/e2e/ --screenshot=on   # save screenshots on failure
```

Playwright test files live in `tests/e2e/`. Use the sync API (`from playwright.sync_api import sync_playwright`) for scripts and the async API with `pytest-playwright` for pytest-based e2e tests.

Example sync script pattern used in this project:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto("http://localhost:8000/")
    page.wait_for_load_state("domcontentloaded")
    page.screenshot(path="screenshot.png")
    browser.close()
```

> The dev server must be running before executing Playwright tests (`uv run python manage.py runserver`).

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

## Git Conventions

Commit messages follow this format:

```
feat: <short imperative summary>

- <bullet describing what changed and why>
- <bullet describing what changed and why>
- ...
```

Common prefixes: `feat:` (new feature), `fix:` (bug fix), `refactor:` (code restructure), `style:` (CSS/UI), `chore:` (config, deps, migrations).

Example:

```
feat: Add base template, signup flow, and product search UI
```

## Roadmap

Planned features to integrate, in rough priority order:

### High priority (fills core gaps)
- **Stripe payment gateway** — orders are placed without real payment; integrate `stripe` for card processing at checkout
- **Order confirmation emails** — send transactional email after checkout using Django's email backend
- **User profile & order history** — `/account/orders/` page for logged-in users to view past orders

### Medium priority
- **Product reviews & ratings** — `Review` model linked to `Product` and `User`
- **Coupon / discount codes** — `Coupon` model with code, discount type (flat/percent), and expiry; applied at checkout
- **Wishlist** — `Wishlist` model linking users to products
- **Social auth (django-allauth)** — Google/GitHub login to reduce signup friction

### Infrastructure
- **Celery + Redis** — async task queue for emails and background order processing
- **django-storages + S3** — replace URL-based product images with real file uploads
- **Django REST Framework (DRF)** — expose store as an API for a future mobile app or React frontend
