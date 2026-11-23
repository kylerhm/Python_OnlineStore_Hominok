from django.contrib import admin
from store.models import Category, Product, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock_quantity", "category", "created_at"]
    list_filter = ["category", "created_at"]
    search_fields = ["name", "description"]
    raw_id_fields = ["category"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at"]
    raw_id_fields = ["user"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["cart", "product", "quantity"]
    raw_id_fields = ["cart", "product"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "status", "total_amount", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["full_name", "email"]
    raw_id_fields = ["user"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "price"]
    raw_id_fields = ["order", "product"]
