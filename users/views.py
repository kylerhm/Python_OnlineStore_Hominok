from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from store.models import Order


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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Регистрация успешна! Теперь вы можете войти.")
            return redirect("users:login")
    else:
        form = UserCreationForm()

    context = {"form": form}
    return render(request, "users/register.html", context)
