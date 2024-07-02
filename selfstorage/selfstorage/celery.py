import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'selfstorage.settings')

app = Celery('selfstorage')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_daily_email_rental_expired': {
        'task': 'storage.tasks.send_daily_email_rental_expired',
        'schedule': crontab(minute="4"),
    },
    'send_daily_email_rental_expires_soon': {
        'task': 'storage.tasks.send_daily_email_rental_expires_soon',
        'schedule': crontab(minute="5"),
    },
    'cancellation_of_order_by_time': {
        'task': 'storage.tasks.cancellation_of_order_by_time',
        'schedule': crontab(minute="10"),
    },
    'delete_old_rents': {
        'task': 'storage.tasks.delete_old_rents',
        'schedule': crontab(minute="30"),
    },
}
