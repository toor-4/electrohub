from .models import Cart, CartItem


class SessionCart:
    def __init__(self, request):
        if not request.session.session_key:
            request.session.create()
        self.session_key = request.session.session_key
        self.cart, _ = Cart.objects.get_or_create(session_key=self.session_key)

    def add(self, product, quantity=1, override_quantity=False):
        item, created = CartItem.objects.get_or_create(
            cart=self.cart,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            if override_quantity:
                item.quantity = quantity
            else:
                item.quantity += quantity
            item.save()
        return item

    def remove(self, product):
        CartItem.objects.filter(cart=self.cart, product=product).delete()

    def update(self, product, quantity):
        if quantity <= 0:
            self.remove(product)
        else:
            CartItem.objects.filter(cart=self.cart, product=product).update(
                quantity=quantity
            )

    def clear(self):
        self.cart.items.all().delete()

    @property
    def items(self):
        return self.cart.items.select_related("product").all()

    @property
    def total(self):
        return self.cart.total

    @property
    def item_count(self):
        return self.cart.item_count
