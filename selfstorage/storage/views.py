from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Min, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.http import urlsafe_base64_encode
# JSONResponse
from django.http import JsonResponse

import datetime

from .tokens import order_confirmation_token
from .forms import UserLoginForm, UserRegistrationForm, UserPasswordResetForm, OrderForm
from .models import Profile, Rent, Order, Box, Rent, Storage

login_form = UserLoginForm()
registration_form = UserRegistrationForm()


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['email'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('storage:account')
                else:
                    messages.error(request, 'Disabled account')
                    return HttpResponse('Disabled account')
            else:
                messages.error(request, 'Invalid login')
                return HttpResponse('Invalid login')
        return render(request, 'index.html', {'login_form': form})
    form = UserLoginForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        user = authenticate(request, username=cd['email'], password=cd['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('storage:account')
            else:
                messages.error(request, 'Disabled account')
                return HttpResponse('Disabled account')
        else:
            messages.error(request, 'Invalid login')
            return HttpResponse('Invalid login')
    return render(request, 'index.html', {'login_form': form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('storage:index')


def user_register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Новый пользователь из формы без загрузки в базу данных
            new_user = user_form.save(commit=False)
            # Установить пароль
            new_user.set_password(
                user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request,
                          'registration/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'registration/register.html',
                  {'form': user_form})


@require_http_methods(['POST'])
def user_password_reset(request):
    form = UserPasswordResetForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        user = authenticate(request, username=cd['email'], password=cd['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('storage:account')
            else:
                messages.error(request, 'Disabled account')
                return HttpResponse('Disabled account')
        else:
            messages.error(request, 'Invalid login')
            return HttpResponse('Invalid login')
    return render(request, 'index.html', {'login_form': form})


@login_required
def view_account(request):
    """ Account page."""
    PERIODS = {
        'День': datetime.timedelta(days=1),
        'Неделя': datetime.timedelta(weeks=1),
        'Месяц': datetime.timedelta(days=30),
        'Год': datetime.timedelta(days=365),
    }

    profile = Profile.objects.get(user=request.user)
    rents = Rent.objects.filter(profile=profile)

    if request.method == 'POST':
        if request.POST.get('duration'):
            extention = request.POST.get('duration')
            rent_id = extention.split(', ')
            period, rent_id = extention.split(', ')
            current_rent = Rent.objects.get(id=rent_id)
            current_rent.end += PERIODS[period]
            current_rent.save()

    context = {
        'profile': profile,
        'rents': list(enumerate(rents, 1)),
        'periods': PERIODS,
    }
    return render(request, 'my-rent.html', context)


def view_index(request):
    """ Main page."""
    qs = Storage.objects.all()
    qs = qs.annotate(
            free_boxes=Count('boxes', filter=Q(boxes__is_active=True)),
            count_boxes=Count('boxes'),
            min_price=Min('boxes__price', )
        ).order_by('?').first()
    context = {
        'storage': qs
    }
    return render(request, 'index.html', context)


def view_boxes(request):
    """ Boxes page."""
    return render(request, 'boxes.html', {
        'login_form': login_form,
        'registration_form': registration_form
    })


def view_storages(request):
    storages = Storage.objects.all()
    storages = storages.annotate(
        free_boxes=Count('boxes', filter=Q(boxes__is_active=True)),
        count_boxes=Count('boxes'),
        min_price=Min('boxes__price', )
    )
    try:
        storage_id = request.GET['storage']
        storage = storages.get(id=storage_id)
    except:
        storage = storages.order_by('?').first()
    boxes = Box.objects.filter(storage=storage)
    return render(request, 'storages.html', {
        'storages': storages,
        'storage': storage,
    })

@require_http_methods(['POST'])
def get_boxes(request):
    """
    return:: JsonResponse
    """
    data = request.POST
    print(data)
    if data:
        storage_id = data['storage_id']
        storage = Storage.objects.get(id=storage_id)
        boxes = Box.objects.filter(storage=storage)
        return JsonResponse({'boxes': boxes})
    else:
        pass


@login_required
# @require_http_methods(['GET', 'POST'])
def create_order(request):

    if request.method == 'POST':
        form = OrderForm(request.POST)
        context = {
            'form': form
        }
        if form.is_valid():
            order = form.save(commit=False)
            order.profile = Profile.objects.get(user=request.user)
            order.box = Box.objects.get(id=request.POST['box_id'])
            uidb64 = urlsafe_base64_encode(str(order.pk).encode())
            url_confirmation = request.build_absolute_uri(
                f"/order_confirm/{uidb64}/{order_confirmation_token.make_token(order)}/"
            )
            order.url_confirmation = url_confirmation
            order.uidb64 = uidb64
            order.save()
            return redirect('storage:order_confirmation_done',)
    else:
        get_data = request.GET
        form = OrderForm()
        context = {
            'form': form,
            'box_id': get_data['box_id'][0]
        }
    return render(request, 'create-order.html', context)


def order_confirmation_done(request):
    return render(request, 'order_confirmation_done.html')


def order_confirm(request, uidb64, token):
    """ Подтверждение заказа. Пользователь перешел по ссылки в письме. """
    order = Order.objects.get(uidb64=uidb64)
    if order is not None and order.status == 2:
        order.status = 3
        order.save()
        return render(request, 'order_confirmed.html', {'order': order})
    else:
        return render(request, 'order_confirm_failed.html')


def view_delivery_partial(request):
    DELIVERY_PRICE = 1250

    if request.POST.get('delivery'):
        rent_id = request.POST.get('delivery')
        current_rent = Rent.objects.get(id=rent_id)
        current_rent.delivery = True
        current_rent.price += DELIVERY_PRICE
        current_rent.save()
    elif request.POST.get('partial'):
        rent_id = request.POST.get('partial')
        current_rent = Rent.objects.get(id=rent_id)
        current_rent.partial = True
        current_rent.save()

    context = {'rent': current_rent}

    return render(request, 'my-rent-delivery-partial.html', context)
