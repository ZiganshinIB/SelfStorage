from celery import shared_task
from .models import Rent, Message
from datetime import datetime, timedelta


@shared_task
def send_daily_email_rental_expired():
    today = datetime.now().date()
    overdue_rents = Rent.objects.filter(end__lt=today, status__in=[1, 3])
    for rent in overdue_rents:
        profile = rent.profile
        email = profile.user.email
        one_month_ago = (datetime.now() - timedelta(days=30)).date()
        old_messages = Message.objects.filter(profile=profile, email=email, created_at__gt=one_month_ago).order_by('-created_at')[:1]
        if not old_messages:
            subject = "Ваша аренда просрочена"
            text = f"Уважаемый {profile.user.first_name} {profile.user.last_name}, \n\n" \
                   f"Срок вашей аренды ящика {rent.box.snumber} истек {rent.end.strftime('%d.%m.%Y')}. " \
                   "Пожалуйста, заберите ваши вещи как можно скорее."
            comments = "Аренда просрочено."
            message = Message(profile=profile, email=email, subject=subject, text=text, comments=comments)
            message.save()
