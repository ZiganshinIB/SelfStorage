# django.core.validators
# from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.models import User


# Форма авторизации User
# <input type="email" required name="EMAIL" class="form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey" placeholder="E-mail">
# <input type="text" required name="PASSWORD" class="form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey" placeholder="Пароль">
class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True, label='E-mail', widget=forms.EmailInput(attrs={
        'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
        'placeholder': 'E-mail',
        'name': 'EMAIL'
    }))
    password = forms.CharField(required=True, label='Password', widget=forms.PasswordInput(attrs={
        'class': 'form-control  border-8 mb-4 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey',
        'placeholder': 'Пароль',
        'name': 'PASSWORD'

    }))


# Форма регистрации User
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',
                                widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data
