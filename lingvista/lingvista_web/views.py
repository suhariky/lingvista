from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ProfileEditForm
from .models import Profile, LanguageLevel, Lesson, Task, UserTasksProgress
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


@login_required
def tasks_view(request, level, lesson):
    # Проверяем, не пройден ли уже урок на 100%
    progress = UserTasksProgress.objects.filter(
        user=request.user,
        level=level.upper(),
        lesson=lesson,
        result=100
    ).first()

    if progress:
        messages.warning(request, 'Вы уже прошли этот урок на 100%!')
        return redirect('lessons', level=level)

    # Остальной код представления остается без изменений
    language_level = get_object_or_404(LanguageLevel, level=level.upper())
    lesson_obj = get_object_or_404(Lesson, language_level=language_level, lesson_number=lesson)
    tasks = list(Task.objects.filter(lesson=lesson_obj).order_by('id'))

    if request.method == 'POST':
        # Проверяем, не пройден ли уже урок
        existing_progress = UserTasksProgress.objects.filter(
            user=request.user,
            level=level.upper(),
            lesson=lesson,
            result=100
        ).exists()

        if existing_progress:
            messages.warning(request, 'Вы уже завершили этот урок!')
            return redirect('lessons', level=level)
        task_results = []
        correct_count = 0

        for task in tasks:
            user_answer = None
            is_correct = False
            correct_answer_display = task.correct_answer

            if task.option1 or task.option2 or task.option3:
                correct_answer = [
                    task.option1,
                    task.option2,
                    task.option3
                ][int(task.correct_answer) - 1]
                user_answer = request.POST.get(f'task_{task.id}')
                is_correct = user_answer == correct_answer

            elif task.audio:
                user_answer = request.POST.get(f'audio_answer_{task.id}', '').strip()
                normalized_user_answer = ' '.join(user_answer.split()).lower()
                normalized_correct = ' '.join(task.correct_answer.split()).lower()
                is_correct = normalized_user_answer == normalized_correct

            if is_correct:
                correct_count += 1

            task_results.append({
                'user_answer': user_answer,
                'is_correct': is_correct,
                "id": task.id,
                'question': task.question,
                'correct_answer': task.correct_answer,
                'option1': task.option1,
                'option2': task.option2,
                'option3': task.option3,
                'audio': task.audio,
            })

        score = int((correct_count / len(tasks)) * 100) if tasks else 0


        # Сохраняем прогресс пользователя
        UserTasksProgress.objects.update_or_create(
            user=request.user,
            level=level.upper(),
            lesson=lesson,
            defaults={'result': score}
        )

        context = {
            'level': level,
            'lesson': lesson,
            'tasks': task_results,
            'show_answers': True,
            'score': score,
            'correct_count': correct_count,
            'lesson_obj': lesson_obj,
        }
        return render(request, 'html/pages/tasks_page.html', context)

    context = {
        'level': level,
        'lesson': lesson,
        'tasks': tasks,
        'show_answers': False,
        'lesson_obj': lesson_obj
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
    # Получаем все уроки для данного уровня
    lessons = Lesson.objects.filter(language_level__level=level.upper()).order_by('lesson_number')

    # Получаем прогресс пользователя по этим урокам
    user_progress = UserTasksProgress.objects.filter(
        user=request.user,
        level=level.upper()
    )

    # Создаем список уроков с информацией о доступности
    lessons_data = []
    for lesson in lessons:
        progress = user_progress.filter(lesson=lesson.lesson_number).first()
        is_completed = progress and progress.result == 100

        lessons_data.append({
            'lesson': lesson,
            'is_completed': is_completed,
            'score': progress.result if progress else 0
        })

    context = {
        'level': level.upper(),
        'lessons_data': lessons_data,
    }
    return render(request, 'html/pages/lessons_page.html', context)

@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'html/pages/account_page.html', {
        'user': request.user,
        'profile': profile,
    })

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
