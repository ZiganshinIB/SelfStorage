from django.contrib import admin
from django.db.models import Count, Min, Q

from .models import Box, Rent, Storage, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'user_email', 'phone', 'photo')
    search_fields = ('user__email', 'phone', 'user__first_name', 'user__last_name')
    fields = ('user', 'phone', 'photo')
    ordering = ('user__pk',)

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


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fields = ('photo', 'phone')


class RentInline(admin.TabularInline):
    model = Rent
    fields = ('box', 'from_city', 'from_street', 'price', 'start', 'end', 'status')
    extra = 0


@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    # /changes/rents/
    fields = (
        'profile',
        'user_full_name',
        'profile_phone',
        'user_email',
        'box',
        'box_price',
        'from_city',
        'from_street',
        'price',
        'end',
        'status')
    readonly_fields = ('user_full_name', 'profile_phone', 'user_email', 'box_price')

    list_display = ('user_full_name', 'box', 'end')
    list_filter = ('end', 'status')
    ordering = ('end',)

    search_fields = ('profile__user__last_name', 'profile__user__first_name', 'box')

    def user_full_name(self, obj):
        return f"{obj.profile.user.first_name} {obj.profile.user.last_name}"
    user_full_name.short_description = 'Польное имя'

    def profile_phone(self, obj):
        return obj.profile.phone
    profile_phone.short_description = 'Телефон'

    def user_email(self, obj):
        return obj.profile.user.email
    user_email.short_description = 'Почта'

    def box_price(self, obj):
        return obj.box.price
    box_price.short_description = 'Цена Ящика'
