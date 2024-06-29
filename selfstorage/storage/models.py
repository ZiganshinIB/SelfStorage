from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
# Отпарвка сообщения
from django.core.mail import send_mail

import requests

from selfstorage.settings import TLY_API_TOKEN

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь',
                                related_name='profile')
    photo = models.ImageField(upload_to='images/profile', verbose_name='Фото', default='images/profile/default.jpg')
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


# TODO: Расмотреть ситуацию с просроченными арендами
# Менеджер аренд для получение актуальных аренд. Не просроченных
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
    from_city = models.CharField(max_length=255, verbose_name='Город', blank=True)
    from_street = models.CharField(max_length=255, verbose_name='Улица', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0)
    start = models.DateTimeField(verbose_name='Начало аренды', auto_now_add=True)
    end = models.DateTimeField(verbose_name='Конец аренды')
    status = models.IntegerField(verbose_name='Статус', choices=RentStatus, null=True)

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

    def clean(self):
        if self.pk:
            original = type(self).objects.get(pk=self.pk)
            if original.field1 != self.field1 or original.field2 != self.field2:
                raise ValueError("Изменение данных запрещено")
        super().clean()

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


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


@receiver(pre_save, sender=Message)
def save_message_box(sender, instance, **kwargs):
    """
    Сохранение сообщение
    При сохранении сообщения - отправляет сообщение на почту
    :param sender:
    :param instance:
    :param kwargs:
    :return:
    """
    send_mail(
        instance.subject,
        instance.text,
        settings.EMAIL_HOST_USER,
        [instance.email],
        fail_silently=False
    )
