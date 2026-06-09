from .cart import SessionCart


def cart_summary(request):
    cart = SessionCart(request)
    return {
        "cart_item_count": cart.item_count,
        "cart_total": cart.total,
    }
