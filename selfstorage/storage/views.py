from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import UserLoginForm, UserRegistrationForm, UserPasswordResetForm, OrderForm
from .models import Profile, Order

login_form = UserLoginForm()
registration_form = UserRegistrationForm()


def user_login(request):
    form = UserLoginForm(request.POST)
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
    return render(request, 'index.html', {
        'login_form': login_form,
        'registration_form': registration_form
    })


def view_boxes(request):
    """ Boxes page."""
    return render(request, 'boxes.html', {
        'login_form': login_form,
        'registration_form': registration_form
    })


@login_required
def view_account(request):
    """ Account page."""

    profile = Profile.objects.get(user=request.user)
    context = {
        'profile': profile
    }
    return render(request, 'my-rent.html', context)


@login_required
#@require_http_methods(['GET', 'POST'])
def create_order(request):
    get_data = request.GET
    print(get_data)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('storage:account')
    else:
        form = OrderForm()
    return render(request, 'create-order.html', {'form': form})
