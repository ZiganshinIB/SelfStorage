from django import template
from django.db.models import Count, Min

from storage.models import Storage, Box


register = template.Library()


@register.simple_tag
def get_storages(storage_id=None):
    storages = Storage.objects.all()
    storages = storages.annotate(
        free_boxes=Count('boxes', filter=Q(boxes__is_active=True)),
        count_boxes=Count('boxes'),
        min_price=Min('boxes__price', )
    )
    if storage_id:
        storage = storages.filter(id=storage_id)
    else:
        storage = storages.order_by('?').first()
    boxes = Box.objects.filter(storage=storage)
    context = {
        'storages': storages,
        'storage': storage,
        'boxes': boxes
    }
    return context


@register.inclusion_tag('hello.html')
def example_include_tag():
    context = {
        'key': 'value',
    }
    return context




