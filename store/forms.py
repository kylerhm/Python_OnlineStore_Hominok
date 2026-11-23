from django import forms

from store.models import Cart, Product


class CartForm(forms.Form):
    """Форма для добавления товара в корзину."""

    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    quantity = forms.IntegerField(
        min_value=1, widget=forms.NumberInput(attrs={"class": "form-control"})
    )


class OrderForm(forms.Form):
    """Форма для оформления заказа."""

    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "ФИО"}),
    )
    address = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 3, "placeholder": "Адрес доставки"}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Телефон"}
        ),
    )
