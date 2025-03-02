from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ProfileEditForm
from .models import Profile


def main_page(request):
    return render(request, 'html/pages/main_page.html')

def login_view(request):
    return render(request, 'html/pages/login_page.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)  # Создаем профиль
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'html/pages/registry_page.html', {'form': form})

def tasks_view(request):
    return render(request, 'html/pages/tasks_page.html')

def profile_view(request):
    return render(request, 'html/pages/account_page.html')

def langlevel_view(request):
    return render(request, 'html/pages/langlevel_page.html')

def accountedit_view(request):
    return render(request, 'html/pages/accountedit_page.html')

def lessons_view(request, level):
    context = {
        'level': level.upper(),
    }
    return render(request, 'html/pages/lessons_page.html', context)

@login_required
def profile(request):
    return render(request, 'user/profile.html', {'user': request.user})

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
    return render(request, 'user/profile_edit.html', {'form': form})

@login_required
def profile_history(request):
    return render(request, 'user/profile_history.html')

