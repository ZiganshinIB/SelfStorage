from django.contrib import admin
from .models import Box, Rent, Storage, Address
from django.db.models import Count, Min, Q


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


