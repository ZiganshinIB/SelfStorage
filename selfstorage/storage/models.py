from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# Create your models here.


class Address(models.Model):
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)


class Storage(models.Model):
    photo = models.ImageField(upload_to='images', verbose_name='Фото')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name='Адрес')
    temperature = models.FloatField(verbose_name='Температура')

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class BoxManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Box(models.Model):
    snumber = models.CharField(max_length=255, verbose_name='Номер ящика', unique=True, db_index=True)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, verbose_name='Склад')
    area = models.FloatField(verbose_name='Площадь')
    dimensions = models.CharField(max_length=255, verbose_name='Размеры')
    price = models.FloatField(verbose_name='Цена')
    is_active = models.BooleanField(verbose_name='Активен', default=True)

    objects = BoxManager()

    class Meta:
        unique_together = [('snumber',)]
        verbose_name = 'Ящик'
        verbose_name_plural = 'Ящики'

    def __str__(self):
        return self.snumber


# TODO: Расмотреть ситуацию с просроченными арендами
# Менеджер аренд для получение актуальных аренд. Не просроченных
class RentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(end__gt=timezone.now())


class Rent(models.Model):
    user = models.ForeignKey(AbstractUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    box = models.ForeignKey(Box, on_delete=models.CASCADE, verbose_name='Ящик')
    start = models.DateTimeField(verbose_name='Начало аренды')
    end = models.DateTimeField(verbose_name='Конец аренды')

    class Meta:
        verbose_name = 'Аренда'
        verbose_name_plural = 'Аренды'

    def __str__(self):
        return self.user
