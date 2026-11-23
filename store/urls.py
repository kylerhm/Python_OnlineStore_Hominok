from django.urls import path
from store import views

app_name = "store"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("category/<int:pk>/", views.category_products, name="category_products"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("cart/update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
]
