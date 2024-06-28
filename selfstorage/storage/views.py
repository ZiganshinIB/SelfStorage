from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth import authenticate, login

from .forms import UserLoginForm, UserRegistrationForm
from .models import Profile

login_form = UserLoginForm()
registration_form = UserRegistrationForm()


# post
@require_http_methods(['POST'])
def user_login(request):
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


@require_http_methods(['POST'])
def user_register(request):
    user_form = UserRegistrationForm(request.POST)
    if user_form.is_valid():

        # Create a new user object but avoid saving it yet
        new_user = user_form.save(commit=False)
        new_user.username = user_form.cleaned_data['email']
        # Set the chosen password
        new_user.set_password(
            user_form.cleaned_data['password'])
        # Save the User object
        new_user.save()
        user = authenticate(request, username=user_form.cleaned_data['email'], password=user_form.cleaned_data['password'])
        login(request, user)
        return redirect('storage:account')


def view_index(request):
    '''Main page.'''
    return render(request, 'index.html', {
        'login_form': login_form,
        'registration_form': registration_form
    })


def view_boxes(request):
    '''Boxes page.'''
    return render(request, 'boxes.html', {
        'login_form': login_form,
        'registration_form': registration_form
    })


def view_account(request):
    '''Account page.'''
    return render(request, 'my-rent.html')
