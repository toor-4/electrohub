from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth import login
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404

from .models import Category, Product, Order, OrderItem
from .forms import UserRegistrationForm, CheckoutForm, ProductSearchForm
from .cart import SessionCart


def home(request):
    featured = Product.objects.filter(is_active=True, is_featured=True)[:8]
    categories = Category.objects.all()
    return render(
        request,
        "store/home.html",
        {
            "featured_products": featured,
            "categories": categories,
        },
    )


def product_list(request):
    form = ProductSearchForm(request.GET)
    products = Product.objects.filter(is_active=True).select_related("category")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        category = form.cleaned_data.get("category")
        min_price = form.cleaned_data.get("min_price")
        max_price = form.cleaned_data.get("max_price")
        sort = form.cleaned_data.get("sort")

        if q:
            products = products.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(brand__icontains=q)
            )
        if category:
            products = products.filter(category=category)
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

        sort_map = {
            "price_asc": "price",
            "price_desc": "-price",
            "name_asc": "name",
            "newest": "-created_at",
        }
        if sort and sort in sort_map:
            products = products.order_by(sort_map[sort])

    total_count = products.count()
    paginator = Paginator(products, 12)
    page = request.GET.get("page")
    products_page = paginator.get_page(page)

    return render(
        request,
        "store/product_list.html",
        {
            "form": form,
            "products": products_page,
            "categories": Category.objects.all(),
            "total_count": total_count,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(
        pk=product.pk
    )[:4]
    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "related": related,
        },
    )


def cart_view(request):
    cart = SessionCart(request)
    return render(request, "store/cart.html", {"cart": cart})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = SessionCart(request)
    quantity = int(request.POST.get("quantity", 1))
    override = request.POST.get("override") == "true"
    cart.add(product, quantity=quantity, override_quantity=override)
    messages.success(request, f"'{product.name}' added to cart.")
    referer = request.META.get("HTTP_REFERER")
    return redirect(referer or "store:product_list")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = SessionCart(request)
    cart.remove(product)
    messages.success(request, "Item removed from cart.")
    return redirect("store:cart")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = SessionCart(request)
    quantity = int(request.POST.get("quantity", 1))
    cart.update(product, quantity)
    return redirect("store:cart")


def checkout(request):
    cart = SessionCart(request)
    if cart.item_count == 0:
        return redirect("store:cart")

    initial = {}
    if request.user.is_authenticated:
        initial["email"] = request.user.email
        initial["full_name"] = (
            f"{request.user.first_name} {request.user.last_name}".strip()
        )

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Stock validation
            stock_error = False
            for item in cart.items:
                if item.product.stock < item.quantity:
                    messages.error(
                        request,
                        f"Sorry, only {item.product.stock} unit(s) of '{item.product.name}' in stock.",
                    )
                    stock_error = True
            if stock_error:
                return render(
                    request, "store/checkout.html", {"form": form, "cart": cart}
                )

            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.total_price = cart.total
            order.save()

            for item in cart.items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_price=item.product.price,
                    quantity=item.quantity,
                )
                item.product.stock -= item.quantity
                item.product.save()

            cart.clear()
            return redirect("store:order_confirm", order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, "store/checkout.html", {"form": form, "cart": cart})


def order_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.user and order.user != request.user:
        raise Http404
    return render(request, "store/order_confirm.html", {"order": order})


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username}!")
            return redirect("store:home")
    else:
        form = UserRegistrationForm()
    return render(request, "store/register.html", {"form": form})
