from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Min, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.utils.http import urlsafe_base64_encode
# JSONResponse
from django.http import JsonResponse

from .tokens import order_confirmation_token

from .forms import UserLoginForm, UserRegistrationForm, UserPasswordResetForm, OrderForm
from .models import Profile, Order, Box, Rent, Storage

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
def view_account(request):
    """ Account page."""

    profile = Profile.objects.get(user=request.user)
    context = {
        'profile': profile
    }
    return render(request, 'my-rent.html', context)
