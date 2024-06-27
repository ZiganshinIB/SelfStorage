from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, resolve_url
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from .forms import UserLoginForm

login_form = UserLoginForm()

# post
@require_http_methods(['POST'])
def user_login(request):
    form = UserLoginForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        user = authenticate(request, username=cd['email'], password=cd['password'])
        if user is not None:
            if user.is_active:
                print(user)
                login(request, user)
                return redirect('storage:account')
            else:
                return HttpResponse('Disabled account')
        else:
            return HttpResponse('Invalid login')
    return render(request, 'index.html', {'login_form': form})



def view_index(request):
    '''Main page.'''
    return render(request, 'index.html', {'login_form': login_form})


def view_boxes(request):
    '''Boxes page.'''
    return render(request, 'boxes.html', {'login_form': login_form})


def view_account(request):
    '''Account page.'''
    return render(request, 'my-rent.html')
