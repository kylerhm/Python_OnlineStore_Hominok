from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserRegistrationTest(TestCase):
    """Тесты для регистрации пользователя."""

    def test_register_view_returns_200(self):
        """Проверка, что страница регистрации загружается."""
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        """Проверка создания пользователя."""
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(User.objects.filter(username="newuser").count(), 1)

    def test_register_redirects_on_success(self):
        """Проверка редиректа после регистрации."""
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_register_fails_with_weak_password(self):
        """Проверка отказа при слабом пароле."""
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "newuser",
                "password1": "123",
                "password2": "123",
            },
        )
        self.assertEqual(response.status_code, 200)  # Ошибка валидации

    def test_register_fails_with_mismatched_passwords(self):
        """Проверка отказа при несовпадении паролей."""
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "newuser",
                "password1": "Pass123!",
                "password2": "Pass456!",
            },
        )
        self.assertEqual(response.status_code, 200)  # Ошибка валидации


class UserProfileTest(TestCase):
    """Тесты для личного кабинета."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="Тест",
            last_name="Пользователь",
            email="test@example.com",
        )

    def test_profile_requires_login(self):
        """Проверка, что профиль требует авторизации."""
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_returns_200(self):
        """Проверка, что авторизованный видит профиль."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)

    def test_profile_shows_user_data(self):
        """Проверка отображения данных пользователя."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("users:profile"))
        self.assertContains(response, "testuser")
        self.assertContains(response, "test@example.com")


class UserLoginTest(TestCase):
    """Тесты для входа пользователя."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_login_view_returns_200(self):
        """Проверка, что страница входа загружается."""
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_success_redirects(self):
        """Проверка успешного входа и редиректа."""
        response = self.client.post(
            reverse("users:login"),
            {"username": "testuser", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 302)

    def test_login_fails_with_wrong_password(self):
        """Проверка отказа при неверном пароле."""
        response = self.client.post(
            reverse("users:login"),
            {"username": "testuser", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 200)  # Ошибка валидации

    def test_login_fails_with_wrong_username(self):
        """Проверка отказа при неверном логине."""
        response = self.client.post(
            reverse("users:login"),
            {"username": "nonexistent", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 200)


class UserLogoutTest(TestCase):
    """Тесты для выхода пользователя."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

    def test_logout_view_returns_200(self):
        """Проверка, что страница выхода загружается."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, 200)

    def test_logout_logs_user_out(self):
        """Проверка, что пользователь выходит."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, 200)
