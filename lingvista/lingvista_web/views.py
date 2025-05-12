from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .check_answer import get_check_strategy
from .forms import CustomPasswordChangeForm, EmailChangeForm, ProfileEditForm, UserLogInForm, UserRegistrationForm
from .models import LanguageLevel, Lesson, Profile, Task, UserTasksProgress


def main_page(request):
    return render(request, 'html/pages/main_page.html')


def policy_view(request):
    return render(request, 'html/pages/policy_page.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('main_page')
        else:
            messages.error(request, 'Invalid username or password')
    form = UserLogInForm(request.POST if request.method == 'POST' else None)
    return render(request, 'html/pages/login_page.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration is successful!')
            return redirect('main_page')
    else:
        form = UserRegistrationForm()
    return render(request, 'html/pages/registry_page.html', {'form': form})


@login_required
def tasks_view(request, level, lesson):
    # Проверка завершенности урока (остается без изменений)
    progress = UserTasksProgress.objects.filter(
        user=request.user, level=level.upper(), lesson=lesson, result=100
    ).first()
    if progress:
        messages.warning(request, 'You have already passed this lesson 100%!!')
        return redirect('lessons', level=level)

    language_level = get_object_or_404(LanguageLevel, level=level.upper())
    lesson_obj = get_object_or_404(Lesson, language_level=language_level, lesson_number=lesson)
    tasks = list(Task.objects.filter(lesson=lesson_obj).order_by('id'))

    if request.method == 'POST':
        if UserTasksProgress.objects.filter(user=request.user, level=level.upper(), lesson=lesson, result=100).exists():
            messages.warning(request, 'You have already completed this lesson!')
            return redirect('lessons', level=level)

        task_results = []
        correct_count = 0

        for task in tasks:
            field, strategy = get_check_strategy(task)
            user_answer = request.POST.get(f'{field}_{task.id}', '').strip()
            is_correct = strategy.check_answer(task, user_answer)

            if is_correct:
                correct_count += 1

            task_results.append(
                {
                    'user_answer': user_answer,
                    'is_correct': is_correct,
                    "id": task.id,
                    'question': task.question,
                    'correct_answer': task.correct_answer,
                    'option1': task.option1,
                    'option2': task.option2,
                    'option3': task.option3,
                    'audio': task.audio,
                }
            )

        score = int((correct_count / len(tasks)) * 100) if tasks else 0

        if score >= 70:
            current_level = language_level.level
            level_order = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
            if current_level in level_order:
                index = level_order.index(current_level)
                if index < len(level_order) - 1:
                    next_level = level_order[index + 1]
                    if not UserTasksProgress.objects.filter(user=request.user, level=next_level).exists():
                        messages.info(request, f'Congratulations! Level {next_level} is open to you!')

        UserTasksProgress.objects.update_or_create(
            user=request.user, level=level.upper(), lesson=lesson, defaults={'result': score}
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

    context = {'level': level, 'lesson': lesson, 'tasks': tasks, 'show_answers': False, 'lesson_obj': lesson_obj}
    return render(request, 'html/pages/tasks_page.html', context)


@login_required
def profile_view(request):
    unlocked_levels = request.user.profile.get_unlocked_levels()
    profile, created = Profile.objects.get_or_create(user=request.user)
    task_progress = UserTasksProgress.objects.filter(user=request.user)
    return render(
        request,
        'html/pages/account_page.html',
        {
            'user': request.user,
            'profile': profile,
            'task_progress': task_progress,
            'language_level': unlocked_levels[-1],
        },
    )


@login_required
def langlevel_view(request):
    unlocked_levels = request.user.profile.get_unlocked_levels()
    all_levels = LanguageLevel.objects.all().order_by('level')

    levels_data = []
    for level in all_levels:
        levels_data.append(
            {
                'level': level,
                'is_unlocked': level.level in unlocked_levels,
                'is_completed': check_level_completion(request.user, level.level),
            }
        )
    return render(request, 'html/pages/langlevel_page.html', {'levels_data': levels_data})


def check_level_completion(user, level):
    lessons = Lesson.objects.filter(language_level__level=level)
    for lesson in lessons:
        progress = UserTasksProgress.objects.filter(user=user, level=level, lesson=lesson.lesson_number).first()
        if not progress or progress.result < 100:
            return False
    return True


# @login_required
# def accountedit_view(request):
#     return render(request, 'html/pages/accountedit_page.html')


@login_required
def lessons_view(request, level):
    # Получаем все уроки для данного уровня
    lessons = Lesson.objects.filter(language_level__level=level.upper()).order_by('lesson_number')

    # Получаем прогресс пользователя по этим урокам
    user_progress = UserTasksProgress.objects.filter(user=request.user, level=level.upper())

    # Создаем список уроков с информацией о доступности
    lessons_data = []
    for lesson in lessons:
        progress = user_progress.filter(lesson=lesson.lesson_number).first()
        is_completed = progress and progress.result == 100

        lessons_data.append(
            {'lesson': lesson, 'is_completed': is_completed, 'score': progress.result if progress else 0}
        )

    context = {
        'level': level.upper(),
        'lessons_data': lessons_data,
    }
    return render(request, 'html/pages/lessons_page.html', context)


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        email_form = EmailChangeForm(request.POST)
        password_form = CustomPasswordChangeForm(request.user, request.POST)

        if 'profile_submit' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile picture has been updated!')
            return redirect('edit_profile')

        if 'email_submit' in request.POST and email_form.is_valid():
            new_email = email_form.cleaned_data['email']
            request.user.email = new_email
            request.user.save()
            messages.success(request, 'Your email has been updated!')
            return redirect('edit_profile')

        if 'password_submit' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Важно, чтобы пользователь не разлогинился
            messages.success(request, 'Your password has been updated!')
            return redirect('edit_profile')
    else:
        profile_form = ProfileEditForm(instance=profile)
        email_form = EmailChangeForm(initial={'email': request.user.email})
        password_form = CustomPasswordChangeForm(request.user)

    return render(
        request,
        'html/pages/accountedit_page.html',
        {
            'profile_form': profile_form,
            'email_form': email_form,
            'password_form': password_form,
        },
    )
