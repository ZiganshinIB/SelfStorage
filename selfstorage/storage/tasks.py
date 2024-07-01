from celery import shared_task
from .models import Rent, Message, Order
from datetime import datetime, timedelta

# TODO: Оптимизировать запросы
@shared_task
def send_daily_email_rental_expired():
    today = datetime.now().date()
    one_month_ago = (datetime.now() - timedelta(days=30)).date()
    comments = "Аренда просрочено."
    overdue_rents = Rent.objects.filter(end__lt=today, status__in=[1, 3])
    for rent in overdue_rents:
        profile = rent.profile
        email = profile.user.email
        text = f"Уважаемый {profile.user.first_name} {profile.user.last_name}, \n\n" \
               f"Срок вашей аренды ящика {rent.box.snumber} истек {rent.end.strftime('%d.%m.%Y')}. " \
               "Пожалуйста, заберите ваши вещи как можно скорее."
        # Направляли ли мы ему ранее письмо?
        old_messages = Message.objects.filter(
            profile=profile,
            email=email,
            created_at__gt=one_month_ago,
            comments=comments,
        ).order_by('-created_at')
        # Если не отправляли уже месяц
        if not old_messages:
            subject = "Ваша аренда просрочена"
            message = Message(profile=profile, email=email, subject=subject, text=text, comments=comments)
            message.save()


# TODO: Очень сложно. Оптимизировать запросы
@shared_task
def send_daily_email_rental_expires_soon():
    today = datetime.now().date()
    comments = "Аренда заканчивается."
    next_month = (datetime.now() + timedelta(days=30)).date()
    mont_ago = (datetime.now() - timedelta(days=30)).date()
    next_two_weeks = (datetime.now() + timedelta(days=14)).date()
    two_weeks_ago = (datetime.now() - timedelta(days=14)).date()
    next_three_days = (datetime.now() + timedelta(days=30)).date()
    three_days_ago = (datetime.now() - timedelta(days=30)).date()
    soon_rents = Rent.objects.filter(end__lte=next_month, status=1)
    next_three_days_rents = soon_rents.filter(end__lt=next_three_days, end__gte=today, status=1)
    for rent in next_three_days_rents:
        profile = rent.profile
        email = profile.user.email
        text = f"Уважаемый {profile.user.first_name} {profile.user.last_name}, \n\n" \
               f"Срок вашей аренды ящика {rent.box.snumber} заканчивается {rent.end.strftime('%d.%m.%Y')}.(Через 3 дня)" \
               "Пожалуйста, заберите ваши вещи как можно скорее."
        old_messages = Message.objects.filter(
            profile=profile,
            email=email,
            created_at__gt=three_days_ago,
            comments=comments
        ).order_by('-created_at')
        if not old_messages:
            print("3 days {}-{}".format(email, rent.box.snumber))
            subject = "Ваша аренда заканчивается"
            message = Message(profile=profile, email=email, subject=subject, text=text, comments=comments)
            message.save()

    next_two_weeks_rents = soon_rents.filter(end__lt=next_two_weeks)
    for rent in next_two_weeks_rents:
        profile = rent.profile
        email = profile.user.email
        text = f"Уважаемый {profile.user.first_name} {profile.user.last_name}, \n\n" \
               f"Срок вашей аренды ящика {rent.box.snumber} заканчивается {rent.end.strftime('%d.%m.%Y')}.(Через 2 недели)" \
               "Пожалуйста, заберите ваши вещи как можно скорее."
        old_messages = Message.objects.filter(
            profile=profile,
            email=email,
            created_at__gt=two_weeks_ago,
            comments=comments,
            text=text
        ).order_by('-created_at')
        if not old_messages:
            print("2 weeks {}-{}".format(email, rent.box.snumber))
            subject = "Ваша аренда заканчивается"
            message = Message(profile=profile, email=email, subject=subject, text=text, comments=comments)
            message.save()

    for rent in soon_rents:
        profile = rent.profile
        email = profile.user.email
        text = f"Уважаемый {profile.user.first_name} {profile.user.last_name}, \n\n" \
               f"Срок вашей аренды ящика {rent.box.snumber} заканчивается {rent.end.strftime('%d.%m.%Y')}.(Через 1 месяц)" \
               "Пожалуйста, заберите ваши вещи как можно скорее."
        old_messages = Message.objects.filter(
            profile=profile,
            email=email,
            created_at__gt=mont_ago,
            comments=comments,
            text=text
        ).order_by('-created_at')[:1]
        if not old_messages:
            print("1 month {}-{}".format(email, rent.box.snumber))
            subject = "Ваша аренда заканчивается"
            message = Message(profile=profile, email=email, subject=subject, text=text, comments=comments)
            message.save()


@shared_task
def cancellation_of_order_by_time():
    # Отмена заказа по истечению срока (1 час)
    today = datetime.now().date() - timedelta(hours=1)
    orders = Order.objects.filter(updated_at__lt=today, status=2)
    for order in orders:
        order.status = 4
        order.save()
