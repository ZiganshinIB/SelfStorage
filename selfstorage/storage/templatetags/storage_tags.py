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
    boxes = Box.objects.filter(storage=storage, is_active=True)
    context = {
        'storages': storages,
        'storage': storage,
        'boxes': boxes
    }
    return context


@register.inclusion_tag('boxes.html')
def boxes(storage_id, area=None):
    storage_id = int(storage_id)
    boxes = Box.objects.filter(storage__pk=storage_id, is_active=True)
    context = {
        'boxes': boxes
    }
    return context




