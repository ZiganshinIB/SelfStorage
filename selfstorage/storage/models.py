import uuid

from django.db import models
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.dispatch import receiver
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image
# Отпарвка сообщения
from django.core.mail import send_mail

import requests

from selfstorage.settings import TLY_API_TOKEN
from .tokens import order_confirmation_token

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь',
                                related_name='profile')
    photo = models.ImageField(
        upload_to='images/profile',
        verbose_name='Фото',
        default='images/profile/default.jpg',
        # blank=True,
        # null=True,
    )
    phone = PhoneNumberField(
        verbose_name='телефон',
        region='RU',
        null=True
    )

    def __str__(self):
        return self.user.last_name + ' ' + self.user.first_name

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'


class Storage(models.Model):
    photo = models.ImageField(upload_to='images', verbose_name='Фото')
    city = models.CharField(max_length=255, verbose_name='Город', blank=True)
    street = models.CharField(max_length=255, verbose_name='Улица', blank=True)
    temperature = models.FloatField(verbose_name='Температура')

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

    def __str__(self):
        return '{} {}'.format(self.city, self.street)


class Box(models.Model):
    snumber = models.CharField(max_length=255, verbose_name='Номер ящика', unique=True, db_index=True)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, verbose_name='Склад', related_name='boxes')
    area = models.FloatField(verbose_name='Площадь')
    dimensions = models.CharField(max_length=255, verbose_name='Размеры')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0)
    is_active = models.BooleanField(verbose_name='Активен', default=True)

    class Meta:
        unique_together = [('snumber',)]
        verbose_name = 'Ящик'
        verbose_name_plural = 'Ящики'

    def __str__(self):
        return self.snumber



class RentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(end__gt=timezone.now())


class Rent(models.Model):
    RentStatus = (
        (1, 'Aрендован'),
        (2, 'Завершена'),
        (3, 'Просрочена'),
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Пользователь')
    box = models.ForeignKey(Box, on_delete=models.CASCADE, verbose_name='Ящик', related_name='rents')
    from_city = models.CharField(max_length=255, verbose_name='Город', blank=True, null=True)
    from_street = models.CharField(max_length=255, verbose_name='Улица', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0)
    start = models.DateTimeField(verbose_name='Начало аренды',)
    end = models.DateTimeField(verbose_name='Конец аренды')
    status = models.IntegerField(verbose_name='Статус', choices=RentStatus, null=True)
    delivery = models.BooleanField(verbose_name='Доставка', default=False)
    partial = models.BooleanField(verbose_name='Частичный забор вещей', default=False)

    class Meta:
        verbose_name = 'Аренда'
        verbose_name_plural = 'Аренды'

    def __str__(self):
        return self.profile.user.last_name + ' ' + self.profile.user.first_name + ' ' + self.box.snumber


class Advertising(models.Model):
    url = models.URLField('Ссылка', blank=True)
    text = models.TextField('Текст рекламы')
    responses = models.IntegerField(
        'Количество откликов',
        null=True,
        blank=True,
        default=0,
    )

    class Meta:
        verbose_name = 'Реклама'
        verbose_name_plural = 'Реклама'


class Message(models.Model):
    """ Сообщение """
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        verbose_name='Пользователь',
        related_name='messages',
        null=True,
        blank=True
    )
    email = models.EmailField('Получатель', max_length=255)
    subject = models.CharField('Тема', max_length=255)
    text = models.TextField('Сообщение')
    comments = models.TextField('Комментарии', null=True, blank=True)


    def __str__(self):
        return "{}: {}".format(self.email, self.subject)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


# Заказ
class Order(models.Model):
    OrderStatus = (
        (1, 'Создан'),
        (2, 'Обработан'),
        (3, 'Подтвержден'),
        (4, 'Отменен'),
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, verbose_name='Пользователь')
    box = models.ForeignKey(
        Box,
        on_delete=models.SET_NULL,
        related_name='orders',
        null=True,
        blank=True,
        verbose_name='Ящик'
    )
    from_city = models.CharField(max_length=255, verbose_name='Город', blank=True)
    from_street = models.CharField(max_length=255, verbose_name='Улица', blank=True)
    has_delivery = models.BooleanField(verbose_name='Доставка', default=False)
    start_rent = models.DateTimeField('Начало аренды')
    end_rent = models.DateTimeField('Конец аренды')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0, null=True, blank=True)
    status = models.IntegerField(verbose_name='Статус', choices=OrderStatus, null=True, default=1)
    url_confirmation = models.URLField('Ссылка подтверждения', null=True, blank=True)
    uidb64 = models.CharField(primary_key=False, editable=False, null=True, blank=True, max_length=255)

    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время обновления', auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at', 'updated_at']

    def __str__(self):
        return f"{self.profile.user.last_name} {self.profile.user.first_name} {self.box.snumber}"

    def send_confirmation_email(self,):
        """ Отправка письма с подтверждением заказа. """
        subject = 'Подтверждение заказа'
        context = {
            'confirmation_url': self.url_confirmation,
            'order': self
        }
        html_message = render_to_string('order_confirmation_email.html', context)
        plain_message = strip_tags(html_message)
        message = Message(profile=self.profile,
                          email=self.profile.user.email,
                          subject=subject,
                          text=plain_message,
                          comments="Подтверждение заказа"
                          )
        message.save()


@receiver(pre_save, sender=Advertising)
def pre_save_advertising(sender, instance, **kwargs):
    if not instance.pk:
        url = "https://t.ly/api/v1/link/shorten"
        headers = {
            "Authorization": f"Bearer {TLY_API_TOKEN}"
        }
        payload = {
            "long_url": "https://www.selfstorage.com/"
        }
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        instance.url = response.json()["short_url"]
        instance.responses = 0


# Создает профиль пользователя при создании пользователя
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance,)


# Сохраняет профиль пользователя
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Rent)
def save_rent_box(sender, instance, **kwargs):
    if instance.status == 1:
        instance.box.is_active = False
    if instance.status == 2:
        instance.box.is_active = True
    if instance.status == 3:
        instance.box.is_active = False
    instance.box.save()


@receiver(pre_delete, sender=Order)
def my_model_deleted(sender, instance, **kwargs):
    if instance.status == 1:
        # Если это новая запись
        if instance.pk is None:
            end_date = instance.end_rent
            start_date = instance.start_rent
            months_difference = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + (
                0 if start_date.day > end_date.day else 1)
            instance.price = instance.box.price * months_difference
        else:
            instance.status = 2
    if instance.status == 2:
        instance.send_confirmation_email()
        instance.box.is_active = False
    if instance.status == 3:
        rent = Rent(
            profile=instance.profile,
            box=instance.box,
            from_city=instance.from_city,
            from_street=instance.from_street,
            status=1,
            price=instance.price,
            start=instance.start_rent,
            end=instance.end_rent
        )
        rent.save()
    if instance.status == 4:
        instance.box.is_active = True
    instance.box.save()

@receiver(pre_delete, sender=Rent)
def my_model_deleted(sender, instance, **kwargs):
    instance.box.is_active = True
    instance.box.save()


@receiver(post_save, sender=Message)
def send_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            instance.subject,
            instance.text,
            settings.EMAIL_HOST_USER,
            [instance.email],
            fail_silently=False,
        )
