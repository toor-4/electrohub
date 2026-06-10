# Component Reference

## Models (`store/models.py`)

- **Category** — top-level product grouping; has a `name`, `slug`, optional `description` and `image` URL; ordered alphabetically
- **Product** — belongs to a `Category`; tracks `name`, `slug`, `brand`, `description`, `price` (decimal), `stock` (int), `image` URL, `is_featured`, `is_active`; `.in_stock` property returns `stock > 0`; ordered newest-first
- **Cart** — one row per browser session, keyed by `session_key` (Django session key); `.total` sums all `CartItem.subtotal` values; `.item_count` sums all quantities
- **CartItem** — join between `Cart` and `Product`; enforces `unique_together` so each product appears at most once per cart; `.subtotal` = `price × quantity`
- **Order** — created at checkout; captures shipping fields (`full_name`, `email`, `phone`, `address_line1/2`, `city`, `postal_code`, `country`), `total_price`, and a `status` field (`pending` → `processing` → `shipped` → `delivered` / `cancelled`); optionally linked to an auth `User` (nullable for guest checkout)
- **OrderItem** — line items for an `Order`; snapshots `product_name` and `product_price` at order time so history is stable if the product changes; `product` FK is nullable (`SET_NULL`) so the row survives product deletion

---

## Cart Layer (`store/cart.py`)

- **SessionCart** — thin wrapper over the `Cart` / `CartItem` models; constructed from a `request` object
  - `__init__` — ensures a session key exists (creates the session if needed), then `get_or_create`s the `Cart` row
  - `.add(product, quantity, override_quantity)` — upserts a `CartItem`; if `override_quantity=True` replaces quantity, otherwise increments it
  - `.remove(product)` — deletes the matching `CartItem`
  - `.update(product, quantity)` — if quantity ≤ 0 calls `.remove`; otherwise issues a direct `UPDATE`
  - `.clear()` — deletes all `CartItem` rows for this cart (called after a successful checkout)
  - `.items` — queryset with `select_related("product")`
  - `.total` / `.item_count` — delegate to `Cart` model properties

---

## Context Processor (`store/context_processors.py`)

- **cart_summary** — registered globally in settings; injects `cart_item_count` and `cart_total` into every template context, powering the header cart badge without any view-level code

---

## Forms (`store/forms.py`)

- **UserRegistrationForm** — extends `UserCreationForm`; adds required `email`, `first_name`, `last_name` fields; `save()` copies those extra fields onto the user instance before writing to DB
- **CheckoutForm** — `ModelForm` backed by `Order`; exposes all shipping / contact fields; `notes` widget is a 3-row `Textarea`
- **ProductSearchForm** — plain `Form` (not model-backed) with fields `q` (text), `category` (FK dropdown), `min_price`, `max_price`, and `sort` (choices: price asc/desc, name asc, newest)

---

## Views (`store/views.py`)

- **home** — fetches up to 8 featured active products and all categories; renders `store/home.html`
- **product_list** — accepts `GET` params via `ProductSearchForm`; filters active products by keyword (name/description/brand), category, and price range; applies sort; paginates at 12 per page
- **product_detail** — looks up product by `slug`; fetches up to 4 related products from the same category
- **cart_view** — wraps `SessionCart` and renders the cart page
- **cart_add** (`POST` only) — adds a product to the cart; redirects back to the referer (or product list)
- **cart_remove** (`POST` only) — removes a product; redirects to cart
- **cart_update** (`POST` only) — updates item quantity; redirects to cart
- **checkout** — `GET` pre-fills email/name if authenticated; `POST` validates stock for each item before creating the `Order` and `OrderItem` rows, decrements `Product.stock`, clears the cart, then redirects to confirmation
- **order_confirm** — shows the confirmation page; raises `Http404` if the order belongs to a different user
- **register** — creates a user via `UserRegistrationForm`, logs them in immediately, and redirects to home

---

## URLs (`store/urls.py`)

All routes use the `store:` namespace.

| Name                   | Path                   | View             |
| ---------------------- | ---------------------- | ---------------- |
| `store:home`           | `/`                    | `home`           |
| `store:product_list`   | `/products/`           | `product_list`   |
| `store:product_detail` | `/products/<slug>/`    | `product_detail` |
| `store:cart`           | `/cart/`               | `cart_view`      |
| `store:cart_add`       | `/cart/add/<id>/`      | `cart_add`       |
| `store:cart_remove`    | `/cart/remove/<id>/`   | `cart_remove`    |
| `store:cart_update`    | `/cart/update/<id>/`   | `cart_update`    |
| `store:checkout`       | `/checkout/`           | `checkout`       |
| `store:order_confirm`  | `/order/<id>/confirm/` | `order_confirm`  |
| `store:register`       | `/register/`           | `register`       |

Auth routes (`/accounts/login/`, `/accounts/logout/`, etc.) come from `django.contrib.auth.urls` and are mounted at `/accounts/` in `demoProject/urls.py`.

---

## Admin (`store/admin.py`)

- **CategoryAdmin** — searchable by name/description; slug auto-populated from name; shows a computed `product_count` column
- **ProductAdmin** — filterable by category/featured/active/brand; `price`, `stock`, `is_featured`, `is_active` are all inline-editable from the list view; date hierarchy on `created_at`
- **CartAdmin** — read-only session key; shows `CartItem` rows via `CartItemInline`
- **OrderAdmin** — `status` is inline-editable from the list; `OrderItem` rows shown via `OrderItemInline`; filterable by status, date, and country
- **OrderItemAdmin** — searchable by `product_name`

---

## Templates

- **`base.html`** — global layout; renders the nav bar with cart badge (from `cart_item_count` context), auth links, and a messages block; all other templates extend this
- **`registration/login.html`** — standard Django auth login form
- **`store/register.html`** — registration form using `UserRegistrationForm`
- **`store/home.html`** — hero section + featured product grid + category tiles
- **`store/product_list.html`** — filter sidebar (`ProductSearchForm`) + paginated product grid; includes `partials/product_card.html` and `partials/pagination.html`
- **`store/product_detail.html`** — full product info, add-to-cart form, related products strip
- **`store/cart.html`** — line-item table with quantity update and remove forms; shows total
- **`store/checkout.html`** — `CheckoutForm` alongside cart summary
- **`store/order_confirm.html`** — thank-you page listing order details and line items
- **`store/partials/product_card.html`** — reusable card component (image, name, price, add-to-cart button)
- **`store/partials/pagination.html`** — page navigation links
- **`store/partials/messages.html`** — Django flash messages rendered as dismissible alerts

---

## Static (`static/css/store.css`)

Single global stylesheet; controls layout, typography, product cards, cart table, form styling, header/nav, and scroll-reveal animation classes applied by the frontend JS.

---

## Management Command (`store/management/commands/seed_data.py`)

- **seed_data** — populates the database with sample categories and products for development; safe to re-run (uses `get_or_create` patterns)

## This covers the following:

- Models — all 6 models with their fields and key properties
- SessionCart — each method and what it does
- Context Processor — how cart_summary injects globals
- Forms — all 3 forms and their purpose
- Views — every view function with its behavior
- URLs — a table of all named routes
- Admin — registered models and notable customizations
- Templates — every template file and what it renders
- Static CSS — quick summary
- seed_data — the management command
