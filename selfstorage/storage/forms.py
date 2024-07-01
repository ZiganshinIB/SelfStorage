from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy
from django.utils import timezone

from .models import Order

UserModel = get_user_model()


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        required=True,
        label=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
            'placeholder': 'E-mail',
            'name': 'EMAIL'
        })
    )
    password = forms.CharField(
        required=True,
        label=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
            'placeholder': 'Пароль',
            'name': 'PASSWORD'
        })
    )

    error_messages = {
        "invalid_login": gettext_lazy(
            "Пожалуйста, введите правильный  %(username)s и пароль. Обратите внимание, что оба"
            "поля могут быть чувствительны к регистру."
        ),
        "inactive": gettext_lazy("Этот аккаунт заблокирован."),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)
        self.username_field = UserModel._meta.get_field(UserModel.EMAIL_FIELD)
        username_max_length = self.username_field.max_length or 254
        self.fields["email"].max_length = username_max_length
        self.fields["email"].widget.attrs["maxlength"] = username_max_length

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(
                self.request, username=email, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"username": "E-mail"},
        )


# Форма регистрации User
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                'placeholder': 'Пароль',
                'name': 'PASSWORD_CREATE'
            }
        )
    )
    password2 = forms.CharField(
        label=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                'placeholder': 'Подтверждение пароля',
                'name': 'PASSWORD_CONFIRM'
            }
        )
    )

    class Meta:
        model = UserModel
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                    'placeholder': 'E-mail',
                    'name': 'EMAIL'
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                    'placeholder': 'Имя',
                    'name': 'FIRST_NAME'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                    'placeholder': 'Фамилия',
                    'name': 'LAST_NAME'
                }
            ),
        }
        # labels empty(False)
        labels = {
            'username': '',
            'email': '',
            'first_name': '',
            'last_name': '',
        }
        # help_texts empty(False)
        help_texts = {
            'username': '',
            'email': '',
            'first_name': '',
            'last_name': '',
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        data = self.cleaned_data['email']
        if UserModel.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                'placeholder': 'E-mail',
                'name': 'EMAIL'
            }
        )
    )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['has_delivery', 'start_rent', 'end_rent', 'from_city', 'from_street']
        widgets = {
            'from_city': forms.TextInput(
                attrs={
                    'type': 'hidden',
                    'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                    'placeholder': 'Город',
                    'name': 'FROM_CITY'
                }
            ),
            'from_street': forms.TextInput(
                attrs={
                    'type': 'hidden',
                    'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                    'placeholder': 'Улица',
                    'name': 'FROM_STREET'
                }
            ),
            'has_delivery': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                    'name': 'HAS_DELIVERY'
                }
            ),
            'start_rent': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                    'placeholder': 'Дата начала аренды',
                    'name': 'START_RENT'
                }
            ),
            'end_rent': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
                    'placeholder': 'Дата окончания аренды',
                    'name': 'END_RENT'
                }
            ),
        }
        labels = {
            'from_city': '',
            'from_street': '',
            'has_delivery': 'Требуется доставка',
            'start_rent': 'начало аренды',
            'end_rent': 'конец аренды',
        }
        help_texts = {
            'from_city': '',
            'from_street': '',
            'has_delivery': '',
            'start_rent': '',
            'end_rent': '',
        }

    def clean_start_rent(self):
        cd = self.cleaned_data
        if cd['start_rent'] < timezone.now():
            raise forms.ValidationError('Начало аренды не может быть меньше сегодняшней даты.')
        return cd['start_rent']

    def clean_end_rent(self):
        cd = self.cleaned_data
        if cd['end_rent'] < timezone.now():
            raise forms.ValidationError('Конец аренды не может быть меньше сегодняшней даты.')
        return cd['end_rent']

    def clean(self):
        cd = self.cleaned_data
        if cd['start_rent'] > cd['end_rent']:
            raise forms.ValidationError('Конец аренды не может быть меньше начала аренды.')
        super().clean()