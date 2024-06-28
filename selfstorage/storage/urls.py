from django.urls import path, reverse_lazy
from django.shortcuts import render, redirect
# auth_views
from django.contrib.auth import views as auth_views
#settings
from django.conf import settings

from . import views
from . import forms
app_name = "storage"

urlpatterns = [
    path('', views.view_index, name='index'),
    path('faq/', render, kwargs={'template_name': 'faq.html'}, name='faq'),
    path('boxes/', views.view_boxes, name='boxes'),
    path('account/', views.view_account, name='account'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    # path('logout/', views.user_logout, name='logout'),
    # Сброс пароля
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
            form_class=forms.UserPasswordResetForm,
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('storage:password_reset_done'),
            from_email=settings.EMAIL_HOST_USER,
         ),
         name='password_reset'),
    # Сброс пароля: После отправки письма
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    # Сброс пароля: Ссылка в письме
    path('password_reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('storage:password_reset_complete'),
         ),
         name='password_reset_confirm'),
    # Сброс пароля: ввод ногового пароля
    path('password_reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
             # success_url=reverse_lazy('storage:login')
         ),
         name='password_reset_complete'),
]
