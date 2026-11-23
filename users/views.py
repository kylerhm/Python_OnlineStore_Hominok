from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from store.models import Order

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Кастомная форма регистрации для кастомной модели пользователя."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")


@login_required
def profile(request):
    """Личный кабинет пользователя."""
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    context = {
        "orders": orders,
    }
    return render(request, "users/profile.html", context)


def register(request):
    """Регистрация нового пользователя."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Регистрация успешна! Теперь вы можете войти.")
            return redirect("users:login")
    else:
        form = CustomUserCreationForm()

    context = {"form": form}
    return render(request, "users/register.html", context)
