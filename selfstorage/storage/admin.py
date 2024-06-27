from django.contrib import admin
from django.db.models import Count, Min, Q

from .models import Box, Rent, Storage, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_email', 'phone')
    search_fields = ('user__email','phone', 'user__first_name', 'user__last_name')
    ordering = ('user',)

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    user_full_name.short_description = 'Польное имя'

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Почта'


@admin.register(Storage)
class StorageAdmin(admin.ModelAdmin):
    list_display = ('city', 'street', 'temperature', 'free_boxes', 'count_boxes', 'min_price')
    search_fields = ('city', 'street',)

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


