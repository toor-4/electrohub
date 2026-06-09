from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse

from store.cart import SessionCart
from store.models import Cart, CartItem, Category, Order, OrderItem, Product

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_request_with_session():
    request = RequestFactory().get("/")
    middleware = SessionMiddleware(get_response=lambda r: r)
    middleware.process_request(request)
    request.session.save()
    return request


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def category(db):
    return Category.objects.create(name="Electronics", slug="electronics")


@pytest.fixture
def product(category):
    return Product.objects.create(
        category=category,
        name="Widget",
        slug="widget",
        description="A test widget",
        price=Decimal("25.00"),
        stock=10,
    )


@pytest.fixture
def cart_model(category):
    return Cart.objects.create(session_key="test-session")


@pytest.fixture
def order(db):
    return Order.objects.create(
        full_name="Jane Doe",
        email="jane@example.com",
        address_line1="123 Main St",
        city="Springfield",
        postal_code="12345",
        total_price=Decimal("30.00"),
    )


@pytest.fixture
def session_cart(product):
    return SessionCart(make_request_with_session())


CHECKOUT_POST = {
    "full_name": "John Smith",
    "email": "john@example.com",
    "phone": "",
    "address_line1": "1 Test St",
    "address_line2": "",
    "city": "Testville",
    "postal_code": "00000",
    "country": "United States",
    "notes": "",
}


# ---------------------------------------------------------------------------
# Model — Product
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_product_in_stock(product):
    assert product.in_stock is True


@pytest.mark.django_db
def test_product_out_of_stock(product):
    product.stock = 0
    product.save()
    product.refresh_from_db()
    assert product.in_stock is False


@pytest.mark.django_db
def test_product_str(product):
    assert str(product) == "Widget"


# ---------------------------------------------------------------------------
# Model — Cart / CartItem
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_empty_cart_total(cart_model):
    assert cart_model.total == 0


@pytest.mark.django_db
def test_empty_cart_item_count(cart_model):
    assert cart_model.item_count == 0


@pytest.mark.django_db
def test_cart_total_with_items(cart_model, product):
    CartItem.objects.create(cart=cart_model, product=product, quantity=3)
    assert cart_model.total == Decimal("75.00")


@pytest.mark.django_db
def test_cart_item_count_with_items(cart_model, product):
    CartItem.objects.create(cart=cart_model, product=product, quantity=3)
    assert cart_model.item_count == 3


@pytest.mark.django_db
def test_cartitem_subtotal(cart_model, product):
    item = CartItem.objects.create(cart=cart_model, product=product, quantity=4)
    assert item.subtotal == Decimal("100.00")


@pytest.mark.django_db
def test_cartitem_str(cart_model, product):
    item = CartItem.objects.create(cart=cart_model, product=product, quantity=2)
    assert str(item) == "2x Widget"


# ---------------------------------------------------------------------------
# Model — Order / OrderItem
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_orderitem_subtotal(order, product):
    item = OrderItem.objects.create(
        order=order,
        product=product,
        product_name="Widget",
        product_price=Decimal("15.00"),
        quantity=2,
    )
    assert item.subtotal == Decimal("30.00")


@pytest.mark.django_db
def test_orderitem_subtotal_uses_snapshot_price(order, product):
    """Changing the live product price must not affect existing order items."""
    item = OrderItem.objects.create(
        order=order,
        product=product,
        product_name="Widget",
        product_price=Decimal("15.00"),
        quantity=2,
    )
    product.price = Decimal("999.00")
    product.save()
    assert item.subtotal == Decimal("30.00")


@pytest.mark.django_db
def test_order_str_contains_name(order):
    assert "Jane Doe" in str(order)


# ---------------------------------------------------------------------------
# SessionCart
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_session_cart_add_new_product(session_cart, product):
    session_cart.add(product, quantity=2)
    assert session_cart.item_count == 2


@pytest.mark.django_db
def test_session_cart_add_accumulates_quantity(session_cart, product):
    session_cart.add(product, quantity=1)
    session_cart.add(product, quantity=3)
    assert session_cart.item_count == 4


@pytest.mark.django_db
def test_session_cart_add_override_replaces_quantity(session_cart, product):
    session_cart.add(product, quantity=5)
    session_cart.add(product, quantity=2, override_quantity=True)
    assert session_cart.item_count == 2


@pytest.mark.django_db
def test_session_cart_remove(session_cart, product):
    session_cart.add(product, quantity=2)
    session_cart.remove(product)
    assert session_cart.item_count == 0


@pytest.mark.django_db
def test_session_cart_update_quantity(session_cart, product):
    session_cart.add(product, quantity=1)
    session_cart.update(product, quantity=5)
    assert session_cart.item_count == 5


@pytest.mark.django_db
def test_session_cart_update_zero_removes_item(session_cart, product):
    session_cart.add(product, quantity=3)
    session_cart.update(product, quantity=0)
    assert session_cart.item_count == 0


@pytest.mark.django_db
def test_session_cart_clear(session_cart, product):
    session_cart.add(product, quantity=3)
    session_cart.clear()
    assert session_cart.item_count == 0


@pytest.mark.django_db
def test_session_cart_total(session_cart, product):
    session_cart.add(product, quantity=3)
    assert session_cart.total == Decimal("75.00")


# ---------------------------------------------------------------------------
# Views — Home
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_home_returns_200(client, product):
    assert client.get(reverse("store:home")).status_code == 200


@pytest.mark.django_db
def test_home_shows_featured_product(client, category):
    Product.objects.create(
        category=category,
        name="Featured Widget",
        slug="featured-widget",
        description="desc",
        price=Decimal("50.00"),
        stock=5,
        is_featured=True,
    )
    assert "Featured Widget" in client.get(reverse("store:home")).content.decode()


# ---------------------------------------------------------------------------
# Views — Product list
# ---------------------------------------------------------------------------


@pytest.fixture
def two_products(category):
    cheap = Product.objects.create(
        category=category,
        name="Cheap Widget",
        slug="cheap-widget",
        description="cheap",
        price=Decimal("10.00"),
        stock=5,
    )
    expensive = Product.objects.create(
        category=category,
        name="Expensive Gadget",
        slug="expensive-gadget",
        description="expensive",
        price=Decimal("200.00"),
        stock=3,
    )
    return cheap, expensive


@pytest.mark.django_db
def test_product_list_returns_200(client, two_products):
    assert client.get(reverse("store:product_list")).status_code == 200


@pytest.mark.django_db
def test_product_list_search(client, two_products):
    r = client.get(reverse("store:product_list"), {"q": "Cheap"})
    content = r.content.decode()
    assert "Cheap Widget" in content
    assert "Expensive Gadget" not in content


@pytest.mark.django_db
def test_product_list_min_price(client, two_products):
    r = client.get(reverse("store:product_list"), {"min_price": "100"})
    content = r.content.decode()
    assert "Expensive Gadget" in content
    assert "Cheap Widget" not in content


@pytest.mark.django_db
def test_product_list_max_price(client, two_products):
    r = client.get(reverse("store:product_list"), {"max_price": "50"})
    content = r.content.decode()
    assert "Cheap Widget" in content
    assert "Expensive Gadget" not in content


@pytest.mark.django_db
def test_product_list_category_filter(client, category, two_products):
    other = Category.objects.create(name="Books", slug="books")
    Product.objects.create(
        category=other,
        name="Django Book",
        slug="django-book",
        description="book",
        price=Decimal("30.00"),
        stock=10,
    )
    r = client.get(reverse("store:product_list"), {"category": category.id})
    assert "Django Book" not in r.content.decode()


@pytest.mark.django_db
def test_product_list_excludes_inactive(client, two_products):
    cheap, _ = two_products
    cheap.is_active = False
    cheap.save()
    assert (
        "Cheap Widget" not in client.get(reverse("store:product_list")).content.decode()
    )


# ---------------------------------------------------------------------------
# Views — Product detail
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_product_detail_returns_200(client, product):
    assert (
        client.get(reverse("store:product_detail", args=[product.slug])).status_code
        == 200
    )


@pytest.mark.django_db
def test_product_detail_shows_name(client, product):
    assert (
        "Widget"
        in client.get(
            reverse("store:product_detail", args=[product.slug])
        ).content.decode()
    )


@pytest.mark.django_db
def test_product_detail_inactive_returns_404(client, product):
    product.is_active = False
    product.save()
    assert (
        client.get(reverse("store:product_detail", args=[product.slug])).status_code
        == 404
    )


@pytest.mark.django_db
def test_product_detail_unknown_slug_returns_404(client, db):
    assert (
        client.get(reverse("store:product_detail", args=["no-such-slug"])).status_code
        == 404
    )


# ---------------------------------------------------------------------------
# Views — Cart
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_cart_view_returns_200(client, db):
    assert client.get(reverse("store:cart")).status_code == 200


@pytest.mark.django_db
def test_cart_add(client, product):
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "2"})
    cart = Cart.objects.get(session_key=client.session.session_key)
    assert cart.item_count == 2


@pytest.mark.django_db
def test_cart_add_accumulates(client, product):
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "1"})
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "3"})
    cart = Cart.objects.get(session_key=client.session.session_key)
    assert cart.item_count == 4


@pytest.mark.django_db
def test_cart_remove(client, product):
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "1"})
    client.post(reverse("store:cart_remove", args=[product.id]))
    cart = Cart.objects.get(session_key=client.session.session_key)
    assert cart.item_count == 0


@pytest.mark.django_db
def test_cart_update(client, product):
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "1"})
    client.post(reverse("store:cart_update", args=[product.id]), {"quantity": "7"})
    cart = Cart.objects.get(session_key=client.session.session_key)
    assert cart.item_count == 7


# ---------------------------------------------------------------------------
# Views — Checkout
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_checkout_empty_cart_redirects(client, db):
    r = client.get(reverse("store:checkout"))
    assert r.status_code == 302
    assert r["Location"] == reverse("store:cart")


@pytest.mark.django_db
def test_checkout_get_with_items(client, product):
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "1"})
    assert client.get(reverse("store:checkout")).status_code == 200


@pytest.mark.django_db
def test_checkout_post_creates_order(client, product):
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "2"})
    client.post(reverse("store:checkout"), CHECKOUT_POST)
    order = Order.objects.first()
    assert order is not None
    assert order.full_name == "John Smith"
    assert order.total_price == Decimal("50.00")


@pytest.mark.django_db
def test_checkout_post_redirects_to_confirm(client, product):
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "1"})
    r = client.post(reverse("store:checkout"), CHECKOUT_POST)
    order = Order.objects.first()
    assert r.status_code == 302
    assert r["Location"] == reverse("store:order_confirm", args=[order.id])


@pytest.mark.django_db
def test_checkout_post_decrements_stock(client, product):
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "3"})
    client.post(reverse("store:checkout"), CHECKOUT_POST)
    product.refresh_from_db()
    assert product.stock == 7


@pytest.mark.django_db
def test_checkout_post_clears_cart(client, product):
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "1"})
    client.post(reverse("store:checkout"), CHECKOUT_POST)
    cart = Cart.objects.get(session_key=client.session.session_key)
    assert cart.item_count == 0


@pytest.mark.django_db
def test_checkout_insufficient_stock_blocks_order(client, product):
    client.post(reverse("store:cart_add", args=[product.id]), {"quantity": "5"})
    product.stock = 2
    product.save()
    r = client.post(reverse("store:checkout"), CHECKOUT_POST)
    assert r.status_code == 200
    assert Order.objects.count() == 0


# ---------------------------------------------------------------------------
# Views — Register
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_register_get(client, db):
    assert client.get(reverse("store:register")).status_code == 200


@pytest.mark.django_db
def test_register_post_creates_user(client, db):
    r = client.post(
        reverse("store:register"),
        {
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "email": "new@example.com",
            "password1": "Str0ng!Pass99",
            "password2": "Str0ng!Pass99",
        },
    )
    assert r.status_code == 302
    assert User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_register_post_invalid_stays_on_page(client, db):
    r = client.post(
        reverse("store:register"),
        {"username": "x", "password1": "short", "password2": "mismatch"},
    )
    assert r.status_code == 200
    assert not User.objects.filter(username="x").exists()
