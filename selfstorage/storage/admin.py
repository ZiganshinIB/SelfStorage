from django.contrib import admin
from django.db.models import Count, Min, Q

import requests
from selfstorage import settings

from .models import Advertising, Box, Rent, Storage, Address, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_email', 'phone')
    search_fields = ('user__email', 'phone', 'user__first_name', 'user__last_name')
    ordering = ('user',)

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    user_full_name.short_description = 'Польное имя'

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Почта'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('pk', 'city', 'street')
    list_display_links = ('pk',)
    list_filter = ('city',)
    search_fields = ('city', 'street')
    ordering = ('city', 'street')


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('address', 'temperature', 'free_boxes', 'count_boxes', 'min_price')
    list_filter = ('address',)
    search_fields = ('address',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
            free_boxes=Count('boxes', filter=Q(boxes__is_active=True)),
            count_boxes=Count('boxes'),
            min_price=Min('boxes__price', )
        )
        return qs

    def free_boxes(self, obj):
        return obj.free_boxes

    def count_boxes(self, obj):
        return obj.count_boxes

    def min_price(self, obj):
        return obj.min_price


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('snumber', 'storage', 'area', 'dimensions', 'price', 'is_active')
    list_filter = ('storage', 'is_active')
    search_fields = ('snumber', 'storage')
    ordering = ('storage', 'snumber')


@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = ('user', 'box', 'start', 'end')
    list_filter = ('user', 'box', 'start', 'end')
    search_fields = ('user', 'box')
    ordering = ('user', 'box')
# Register your models here.


@admin.register(Advertising)
class AdvertisingModel(admin.ModelAdmin):
    list_display = ('url', 'text', 'responses',)
    readonly_fields = ('url', 'responses',)

    def changelist_view(self, request, extra_context=None):
        advertising = Advertising.objects.all()
        headers = {
            "Authorization": f"Bearer {settings.TLY_API_TOKEN}"
        }
        url = "https://t.ly/api/v1/link/stats"
        for ad in advertising:
            params = {"short_url": ad.url}
            response = requests.get(url,
                                    headers=headers,
                                    params=params)
            response.raise_for_status()
            ad.responses = response.json()["clicks"]
        Advertising.objects.bulk_update(advertising, ['responses'])
        return super().changelist_view(request, extra_context=extra_context)
