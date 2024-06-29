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
        'schedule': crontab(minute="47"),
    },
}