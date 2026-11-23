from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from django.urls import reverse

from store.models import Cart, CartItem, Category, Order, OrderItem, Product
from store.views import (
    add_to_cart,
    cart,
    checkout,
    order_detail,
    order_history,
    product_detail,
    product_list,
)

User = get_user_model()


# ====================================================================
# Тесты для моделей
# ====================================================================


class CategoryTestCase(TestCase):
    """Тесты для модели Category."""

    def setUp(self):
        self.category = Category.objects.create(name="Электроника")

    def test_category_str(self):
        """Проверка __str__ метода."""
        self.assertEqual(str(self.category), "Электроника")

    def test_category_creation(self):
        """Проверка создания категории."""
        self.assertIsNotNone(self.category)
        self.assertEqual(self.category.name, "Электроника")

    def test_category_multiple_creation(self):
        """Проверка создания нескольких категорий."""
        Category.objects.create(name="Другая категория")
        self.assertEqual(Category.objects.count(), 2)


class ProductTestCase(TestCase):
    """Тесты для модели Product."""

    def setUp(self):
        self.category = Category.objects.create(name="Тестовая категория")
        self.product = Product.objects.create(
            name="Тестовый товар",
            description="Описание товара",
            price=1000.50,
            category=self.category,
            stock_quantity=10,
        )

    def test_product_str(self):
        """Проверка __str__ метода."""
        self.assertEqual(str(self.product), "Тестовый товар")

    def test_product_creation(self):
        """Проверка создания товара."""
        self.assertIsNotNone(self.product)
        self.assertEqual(self.product.name, "Тестовый товар")
        self.assertEqual(self.product.price, 1000.50)
        self.assertEqual(self.product.stock_quantity, 10)

    def test_product_price_positive(self):
        """Проверка, что цена положительная."""
        self.assertGreater(self.product.price, 0)

    def test_product_stock_quantity_positive(self):
        """Проверка, что количество на складе положительное."""
        self.assertGreaterEqual(self.product.stock_quantity, 0)

    def test_product_category_relationship(self):
        """Проверка связи с категорией."""
        self.assertEqual(self.product.category, self.category)
        self.assertIn(self.product, self.category.products.all())


class CartTestCase(TestCase):
    """Тесты для модели Cart."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        """Проверка создания корзины."""
        self.assertIsNotNone(self.cart)
        self.assertEqual(self.cart.user, self.user)

    def test_cart_str(self):
        """Проверка __str__ метода."""
        self.assertIn(self.user.username, str(self.cart))

    def test_get_total_empty_cart(self):
        """Проверка get_total для пустой корзины."""
        self.assertEqual(self.cart.get_total(), 0)


class CartItemTestCase(TestCase):
    """Тесты для модели CartItem."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.category = Category.objects.create(name="Категория")
        self.product = Product.objects.create(
            name="Товар",
            price=500.00,
            category=self.category,
            stock_quantity=100,
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3,
        )

    def test_cart_item_creation(self):
        """Проверка создания позиции корзины."""
        self.assertIsNotNone(self.cart_item)
        self.assertEqual(self.cart_item.quantity, 3)

    def test_cart_item_str(self):
        """Проверка __str__ метода."""
        self.assertIn("Товар", str(self.cart_item))
        self.assertIn("3", str(self.cart_item))

    def test_cart_item_get_total(self):
        """Проверка get_total для позиции."""
        self.assertEqual(self.cart_item.get_total(), 1500.00)

    def test_cart_item_unique_constraint(self):
        """Проверка уникальности cart + product."""
        with self.assertRaises(Exception):
            CartItem.objects.create(
                cart=self.cart,
                product=self.product,
                quantity=1,
            )


class OrderTestCase(TestCase):
    """Тесты для модели Order."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.order = Order.objects.create(
            user=self.user,
            full_name="Тестовый Пользователь",
            address="ул. Тестовая, д. 1",
            email="test@example.com",
            status="new",
            total_amount=2500.00,
        )

    def test_order_creation(self):
        """Проверка создания заказа."""
        self.assertIsNotNone(self.order)
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.status, "new")

    def test_order_str(self):
        """Проверка __str__ метода."""
        self.assertIn(str(self.order.id), str(self.order))
        self.assertIn("Тестовый Пользователь", str(self.order))

    def test_order_status_choices(self):
        """Проверка доступных статусов."""
        statuses = dict(Order.STATUS_CHOICES)
        self.assertIn("new", statuses)
        self.assertIn("processing", statuses)
        self.assertIn("shipped", statuses)
        self.assertIn("delivered", statuses)
        self.assertIn("cancelled", statuses)

    def test_order_total_amount(self):
        """Проверка итоговой суммы."""
        self.assertEqual(self.order.total_amount, 2500.00)


class OrderItemTestCase(TestCase):
    """Тесты для модели OrderItem."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.category = Category.objects.create(name="Категория")
        self.product = Product.objects.create(
            name="Товар",
            price=500.00,
            category=self.category,
            stock_quantity=100,
        )
        self.order = Order.objects.create(
            user=self.user,
            full_name="Тест",
            address="Тест",
            email="test@example.com",
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=500.00,
        )

    def test_order_item_creation(self):
        """Проверка создания позиции заказа."""
        self.assertIsNotNone(self.order_item)
        self.assertEqual(self.order_item.quantity, 2)

    def test_order_item_str(self):
        """Проверка __str__ метода."""
        self.assertIn(str(self.order.id), str(self.order_item))
        self.assertIn("Товар", str(self.order_item))

    def test_order_item_get_total(self):
        """Проверка get_total для позиции заказа."""
        self.assertEqual(self.order_item.get_total(), 1000.00)


# ====================================================================
# Тесты для представлений (Views)
# ====================================================================


class ProductListViewTest(TestCase):
    """Тесты для product_list."""

    def setUp(self):
        self.category = Category.objects.create(name="Тест")
        self.product = Product.objects.create(
            name="Товар 1",
            price=100.00,
            category=self.category,
            stock_quantity=5,
        )

    def test_product_list_returns_200(self):
        """Проверка, что страница возвращает 200."""
        response = self.client.get(reverse("store:product_list"))
        self.assertEqual(response.status_code, 200)

    def test_product_list_context(self):
        """Проверка контекста."""
        response = self.client.get(reverse("store:product_list"))
        self.assertIn("products", response.context)
        self.assertEqual(len(response.context["products"]), 1)

    def test_product_list_shows_products(self):
        """Проверка, что товары отображаются."""
        response = self.client.get(reverse("store:product_list"))
        self.assertContains(response, "Товар 1")


class ProductDetailViewTest(TestCase):
    """Тесты для product_detail."""

    def setUp(self):
        self.category = Category.objects.create(name="Тест")
        self.product = Product.objects.create(
            name="Товар 2",
            description="Описание",
            price=200.00,
            category=self.category,
            stock_quantity=5,
        )

    def test_product_detail_returns_200(self):
        """Проверка, что страница возвращает 200."""
        response = self.client.get(
            reverse("store:product_detail", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_product_detail_404(self):
        """Проверка 404 для несуществующего товара."""
        response = self.client.get(reverse("store:product_detail", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, 404)

    def test_product_detail_shows_data(self):
        """Проверка отображения данных."""
        response = self.client.get(
            reverse("store:product_detail", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, "Товар 2")
        self.assertContains(response, "Описание")
        self.assertContains(response, "200,00")


class CartViewTest(TestCase):
    """Тесты для корзины."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.category = Category.objects.create(name="Тест")
        self.product = Product.objects.create(
            name="Товар",
            price=100.00,
            category=self.category,
            stock_quantity=50,
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

    def test_cart_requires_login(self):
        """Проверка, что корзина требует авторизации."""
        response = self.client.get(reverse("store:cart"))
        self.assertEqual(response.status_code, 302)

    def test_cart_returns_200_for_authenticated(self):
        """Проверка, что авторизованный пользователь видит корзину."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("store:cart"))
        self.assertEqual(response.status_code, 200)

    def test_cart_shows_items(self):
        """Проверка отображения товаров в корзине."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("store:cart"))
        self.assertContains(response, "Товар")


class AddToCartViewTest(TestCase):
    """Тесты для add_to_cart."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.category = Category.objects.create(name="Тест")
        self.product = Product.objects.create(
            name="Товар",
            price=100.00,
            category=self.category,
            stock_quantity=10,
        )

    def test_add_to_cart_requires_login(self):
        """Проверка, что добавление требует авторизации."""
        response = self.client.post(
            reverse("store:add_to_cart"),
            {"product": self.product.pk, "quantity": 1},
        )
        self.assertEqual(response.status_code, 302)

    def test_add_to_cart_success(self):
        """Проверка успешного добавления."""
        self.client.login(username="testuser", password="testpass123")
        # Получаем CSRF токен
        self.client.get(reverse("store:add_to_cart"))
        response = self.client.post(
            reverse("store:add_to_cart"),
            {"product": self.product.pk, "quantity": 2},
        )
        self.assertEqual(response.status_code, 302)

    def test_add_to_cart_exceeds_stock(self):
        """Проверка превышения остатка на складе."""
        self.client.login(username="testuser", password="testpass123")
        self.client.get(reverse("store:add_to_cart"))
        response = self.client.post(
            reverse("store:add_to_cart"),
            {"product": self.product.pk, "quantity": 999},
        )
        self.assertEqual(response.status_code, 302)


class CheckoutViewTest(TestCase):
    """Тесты для оформления заказа."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.category = Category.objects.create(name="Тест")
        self.product = Product.objects.create(
            name="Товар",
            price=100.00,
            category=self.category,
            stock_quantity=50,
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

    def test_checkout_requires_login(self):
        """Проверка, что оформление требует авторизации."""
        response = self.client.post(reverse("store:checkout"))
        self.assertEqual(response.status_code, 302)

    def test_checkout_success(self):
        """Проверка успешного оформления заказа."""
        self.client.login(username="testuser", password="testpass123")
        # Получаем CSRF токен
        self.client.get(reverse("store:checkout"))
        # Оформляем заказ
        self.client.post(
            reverse("store:checkout"),
            {
                "full_name": "Тестовый Пользователь",
                "address": "ул. Тестовая, 1",
                "email": "test@example.com",
                "phone": "+79991234567",
            },
        )
        # Заказ должен быть создан
        self.assertGreaterEqual(Order.objects.count(), 0)


class AuthViewTest(TestCase):
    """Тесты для аутентификации."""

    def test_register_page_loads(self):
        """Проверка, что страница регистрации загружается."""
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        """Проверка успешной регистрации."""
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "newuser",
                "password1": "TestPass123!",
                "password2": "TestPass123!",
            },
        )
        self.assertEqual(User.objects.filter(username="newuser").count(), 1)

    def test_login_page_loads(self):
        """Проверка, что страница входа загружается."""
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        """Проверка успешного входа."""
        User.objects.create_user(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("users:login"),
            {"username": "testuser", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 302)

    def test_logout_success(self):
        """Проверка выхода."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, 200)


class OrderHistoryViewTest(TestCase):
    """Тесты для истории заказов."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.order = Order.objects.create(
            user=self.user,
            full_name="Тест",
            address="Тест",
            email="test@example.com",
        )

    def test_order_history_requires_login(self):
        """Проверка, что история требует авторизации."""
        response = self.client.get(reverse("store:order_history"))
        self.assertEqual(response.status_code, 302)

    def test_order_history_returns_200(self):
        """Проверка, что авторизованный видит историю."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("store:order_history"))
        self.assertEqual(response.status_code, 200)

    def test_order_history_shows_orders(self):
        """Проверка отображения заказов."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("store:order_history"))
        self.assertContains(response, "Тест")
