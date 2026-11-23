from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from store.forms import CartForm, OrderForm
from store.models import Cart, CartItem, Category, Order, OrderItem, Product


def product_list(request):
    """Отображение списка всех товаров."""
    products = Product.objects.all()
    categories = Category.objects.all()
    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "store/product_list.html", context)


def product_detail(request, pk):
    """Отображение карточки товара."""
    product = get_object_or_404(Product, pk=pk)
    context = {"product": product}
    return render(request, "store/product_detail.html", context)


def category_products(request, pk):
    """Отображение товаров категории."""
    category = get_object_or_404(Category, pk=pk)
    products = category.products.all()
    context = {
        "products": products,
        "category": category,
    }
    return render(request, "store/product_list.html", context)


@login_required
def add_to_cart(request):
    """Добавление товара в корзину."""
    if request.method == "POST":
        form = CartForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]

            # Проверяем наличие на складе
            if product.stock_quantity < quantity:
                messages.error(
                    request, f"На складе доступно только {product.stock_quantity} шт."
                )
                return redirect("store:product_detail", pk=product.pk)

            # Получаем или создаём корзину пользователя
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Добавляем или обновляем позицию
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
            )
            if not created:
                cart_item.quantity += quantity
            cart_item.quantity = quantity
            cart_item.save()

            messages.success(request, f"{product.name} добавлен в корзину")
            return redirect("store:cart")
    else:
        form = CartForm()

    context = {"form": form}
    return render(request, "store/add_to_cart.html", context)


@login_required
def cart(request):
    """Отображение корзины."""
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()
    total = cart.get_total()

    context = {
        "cart": cart,
        "items": items,
        "total": total,
    }
    return render(request, "store/cart.html", context)


@login_required
def update_cart_item(request, item_id):
    """Обновление количества товара в корзине."""
    if request.method == "POST":
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)

        try:
            quantity = int(request.POST.get("quantity", 1))
            if quantity < 1:
                item.delete()
            else:
                # Проверяем наличие на складе
                if item.product.stock_quantity < quantity:
                    messages.error(
                        request,
                        f"На складе доступно только {item.product.stock_quantity} шт.",
                    )
                    return redirect("cart")
                item.quantity = quantity
                item.save()
        except (ValueError, TypeError):
            item.delete()

        return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    """Удаление товара из корзины."""
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    return redirect("cart")


@login_required
def checkout(request):
    """Оформление заказа."""
    cart = get_object_or_404(Cart, user=request.user)

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Проверяем наличие всех товаров на складе
            for item in cart.items.all():
                if item.product.stock_quantity < item.quantity:
                    messages.error(
                        request,
                        f"На складе недостаточно {item.product.name} (доступно: {item.product.stock_quantity})",
                    )
                    return redirect("cart")

            try:
                with transaction.atomic():
                    # Создаём заказ
                    order = Order.objects.create(
                        user=request.user,
                        full_name=form.cleaned_data["full_name"],
                        address=form.cleaned_data["address"],
                        email=form.cleaned_data["email"],
                        phone=form.cleaned_data["phone"],
                        total_amount=cart.get_total(),
                    )

                    # Создаём позиции заказа и уменьшаем остатки
                    for item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price,
                        )
                        item.product.stock_quantity -= item.quantity
                        item.product.save()

                    # Очищаем корзину
                    cart.items.all().delete()

                    messages.success(request, "Заказ успешно оформлен!")
                    return redirect("order_history")
            except Exception as e:
                messages.error(request, f"Ошибка при оформлении заказа: {e}")
    else:
        form = OrderForm()

    context = {
        "form": form,
        "cart": cart,
        "items": cart.items.all(),
        "total": cart.get_total(),
    }
    return render(request, "store/checkout.html", context)


@login_required
def order_history(request):
    """История заказов пользователя."""
    orders = Order.objects.filter(user=request.user)
    context = {"orders": orders}
    return render(request, "store/order_history.html", context)


@login_required
def order_detail(request, pk):
    """Детали заказа."""
    order = get_object_or_404(Order, pk=pk, user=request.user)
    items = order.items.all()
    context = {
        "order": order,
        "items": items,
    }
    return render(request, "store/order_detail.html", context)
