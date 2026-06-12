# Django E-Commerce Store

A Django 5.2 e-commerce application with product browsing, a session-backed cart, and order checkout.

## Requirements

- Python 3.10+

## Setup

```bash
# Create and activate a virtual environment
python3.10 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# (Optional) Seed sample data
python manage.py seed_data

# Create an admin superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver
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
├── demoProject/                  # Django project package
│   ├── settings.py               # Configuration (DB, auth, static, context processors)
│   ├── urls.py                   # Root URLconf (admin + auth + store)
│   ├── wsgi.py / asgi.py
│
├── store/                        # Main application
│   ├── models.py                 # Category, Product, Cart, CartItem, Order, OrderItem
│   ├── views.py                  # home, product_list/detail, cart_*, checkout, order_confirm, register
│   ├── cart.py                   # SessionCart — session-keyed DB cart wrapper
│   ├── forms.py                  # UserRegistrationForm, CheckoutForm, ProductSearchForm
│   ├── urls.py                   # All store: routes
│   ├── admin.py                  # Admin registrations with inlines
│   ├── context_processors.py     # cart_summary — injects cart_item_count/cart_total globally
│   ├── tests.py                  # pytest suite (47 tests)
│   └── management/commands/
│       └── seed_data.py          # Populates sample categories and products
│
├── templates/
│   ├── base.html                 # Global layout: nav, messages, footer
│   ├── registration/
│   │   └── login.html
│   └── store/
│       ├── home.html             # Hero, category pills, featured products, CTA
│       ├── product_list.html     # Filter sidebar + paginated product grid
│       ├── product_detail.html   # Product info, add-to-cart, related products
│       ├── cart.html             # Line-item table, order summary
│       ├── checkout.html         # Shipping form + order summary
│       ├── order_confirm.html    # Post-order confirmation
│       ├── register.html
│       └── partials/
│           ├── product_card.html
│           ├── pagination.html
│           └── messages.html
│
├── static/css/store.css          # Volt Dark design system (CSS custom properties + Bootstrap overrides)
├── requirements.txt              # Pinned production dependencies
├── requirements-dev.txt          # Pinned dev dependencies (pytest, ruff)
├── tests/e2e/                    # Playwright end-to-end tests
└── COMPONENTS.md                 # Component reference with field-level detail
```

## Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run verbose
pytest -v
```

## Deploying to PythonAnywhere

### 1. Create a PythonAnywhere account

Sign up at [pythonanywhere.com](https://www.pythonanywhere.com) (the free "Beginner" tier works for evaluation).

### 2. Open a Bash console

From the **Dashboard → Consoles**, start a new **Bash** console.

### 3. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 4. Create a virtual environment and install dependencies

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Set environment variables

Create a `.env` file (or export directly in the console):

```bash
export DJANGO_SECRET_KEY='replace-with-a-long-random-string'
export DJANGO_DEBUG='False'
export DJANGO_ALLOWED_HOSTS='<your-username>.pythonanywhere.com'
```

> To generate a secret key: `python -c "import secrets; print(secrets.token_urlsafe(50))"`

### 6. Apply migrations and collect static files

```bash
python manage.py migrate
python manage.py collectstatic --noinput

# Optional: seed sample data
python manage.py seed_data
```

### 7. Configure the web app

1. Go to **Web** tab → **Add a new web app**
2. Choose **Manual configuration** → **Python 3.10**
3. Set the **Virtualenv** path to `/home/<your-username>/<your-repo>/venv`

### 8. Edit the WSGI file

Click the WSGI file link (e.g. `/var/www/<your-username>_pythonanywhere_com_wsgi.py`) and replace its contents with:

```python
import os
import sys

path = '/home/<your-username>/<your-repo>'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SECRET_KEY'] = 'replace-with-your-secret-key'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = '<your-username>.pythonanywhere.com'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demoProject.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 9. Configure static files

In the **Web** tab under **Static files**, add:

| URL       | Directory                                      |
|-----------|------------------------------------------------|
| `/static/`| `/home/<your-username>/<your-repo>/staticfiles/`|

### 10. Reload and open

Click **Reload** in the Web tab, then visit:

```
https://<your-username>.pythonanywhere.com
```

### Updating after a git push

```bash
cd ~/<your-repo>
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then click **Reload** in the Web tab.
