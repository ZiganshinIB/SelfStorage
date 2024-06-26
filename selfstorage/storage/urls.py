from django.urls import path
from django.shortcuts import render

from . import views

app_name = "storage"

urlpatterns = [
    path('', views.view_index, name='index'),
    path('faq/', render, kwargs={'template_name': 'faq.html'}, name='faq'),
    path('boxes/', views.view_boxes, name='boxes'),
]
