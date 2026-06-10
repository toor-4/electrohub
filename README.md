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
# Run all tests
uv run pytest

# Run verbose
uv run pytest -v
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
python3.12 -m venv .venv
source .venv/bin/activate
pip install uv
uv sync --no-dev
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
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput

# Optional: seed sample data
uv run python manage.py seed_data
```

### 7. Configure the web app

1. Go to **Web** tab → **Add a new web app**
2. Choose **Manual configuration** → **Python 3.12**
3. Set the **Virtualenv** path to `/home/<your-username>/<your-repo>/.venv`

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
source .venv/bin/activate
uv sync --no-dev
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
```

Then click **Reload** in the Web tab.
