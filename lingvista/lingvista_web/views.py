from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ProfileEditForm
from .models import Profile
from django.views.decorators.http import require_POST

@require_POST
def custom_logout(request):
    logout(request)
    return redirect('main_page')

def main_page(request):
    return render(request, 'html/pages/main_page.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('main_page')
        else:
            messages.error(request, 'Неверные имя пользователя или пароль')
    return render(request, 'html/pages/login_page.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('main_page')  # Исправлен редирект
    else:
        form = UserRegistrationForm()
    return render(request, 'html/pages/registry_page.html', {'form': form})

#@login_required
def tasks_view(request, lesson):
    context = {
        'lesson': lesson,
    }
    return render(request, 'html/pages/tasks_page.html', context)

@login_required
def profile_view(request):
    return render(request, 'html/pages/account_page.html')

@login_required
def langlevel_view(request):
    return render(request, 'html/pages/langlevel_page.html')

@login_required
def accountedit_view(request):
    return render(request, 'html/pages/accountedit_page.html')

@login_required
def lessons_view(request, level):
    context = {
        'level': level.upper(),
    }
    return render(request, 'html/pages/lessons_page.html', context)

@login_required
def profile(request):
    return render(request, 'html/pages/account_page.html', {'user': request.user})

@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'html/pages/accountedit_page.html', {'form': form})

@login_required
def profile_history(request):
    return render(request, 'html/pages/profile_history.html')
