from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

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


class Address(models.Model):
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'

    def __str__(self):
        return f'{self.city}, {self.street}'


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
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, verbose_name='Склад', related_name='boxes')
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
    RentStatus = (
        (1, 'Aрендован'),
        (2, 'Завершена'),
        (3, 'Просрочена'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    box = models.ForeignKey(Box, on_delete=models.CASCADE, verbose_name='Ящик')
    start = models.DateTimeField(verbose_name='Начало аренды', auto_now_add=True)
    end = models.DateTimeField(verbose_name='Конец аренды')
    status = models.IntegerField(verbose_name='Статус', choices=RentStatus, null=True)

    class Meta:
        verbose_name = 'Аренда'
        verbose_name_plural = 'Аренды'

    def __str__(self):
        return self.user


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance,)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
