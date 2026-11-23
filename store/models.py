from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Category(models.Model):
    """Категория товаров."""

    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(max_length=255, blank=True, verbose_name="URL")

    class Meta:
        db_table = "store_category"
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар."""

    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Цена"
    )
    image = models.ImageField(
        upload_to="products/",
        blank=True,
        verbose_name="Изображение"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категория"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Остаток на складе"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = "store_product"
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Cart(models.Model):
    """Корзина пользователя."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = "store_cart"
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина пользователя {self.user.get_full_name() or self.user.username}"

    def get_total(self):
        """Вычислить общую стоимость корзины."""
        return sum(item.get_total() for item in self.items.all())


class CartItem(models.Model):
    """Позиция корзины."""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Количество",
        validators=[MinValueValidator(1)]
    )

    class Meta:
        db_table = "store_cart_item"
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"
        unique_together = ["cart", "product"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total(self):
        """Вычислить стоимость позиции."""
        return self.product.price * self.quantity


class Order(models.Model):
    """Заказ."""

    STATUS_CHOICES = [
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменён"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Пользователь"
    )
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    address = models.TextField(verbose_name="Адрес доставки")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Итого"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = "store_order"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    """Позиция заказа."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Количество"
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        verbose_name="Цена за единицу"
    )

    class Meta:
        db_table = "store_order_item"
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"Заказ #{self.order.id}: {self.product.name} x {self.quantity}"

    def get_total(self):
        """Вычислить стоимость позиции."""
        return self.price * self.quantity
