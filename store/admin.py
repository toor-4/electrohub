from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "product_count", "created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = "Products"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "brand",
        "price",
        "stock",
        "is_featured",
        "is_active",
        "created_at",
    ]
    list_filter = ["category", "is_featured", "is_active", "brand"]
    search_fields = ["name", "description", "brand"]
    list_editable = ["price", "stock", "is_featured", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    date_hierarchy = "created_at"


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["product", "quantity"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["session_key", "item_count_display", "created_at"]
    readonly_fields = ["session_key", "created_at", "updated_at"]
    inlines = [CartItemInline]

    def item_count_display(self, obj):
        return obj.items.count()

    item_count_display.short_description = "Items"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "product_name", "product_price", "quantity"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "full_name", "email", "total_price", "status", "created_at"]
    list_filter = ["status", "created_at", "country"]
    search_fields = ["full_name", "email", "phone", "address_line1"]
    list_editable = ["status"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product_name", "product_price", "quantity"]
    search_fields = ["product_name"]
