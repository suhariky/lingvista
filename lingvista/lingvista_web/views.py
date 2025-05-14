from typing import Any, Dict, List, Literal, TypedDict, Union

from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from .check_answer import get_check_strategy
from .forms import (
    CustomPasswordChangeForm,
    EmailChangeForm,
    ProfileEditForm,
    UserLogInForm,
    UserRegistrationForm,
)
from .models import LanguageLevel, Lesson, Profile, Task, UserTasksProgress

# Тип для уровней языка (A1, A2, B1, B2, C1, C2)
LanguageLevelType = Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2']


class TaskResult(TypedDict):
    """Типизированный словарь для хранения результатов выполнения задания."""

    user_answer: str
    is_correct: bool
    id: int
    question: str
    correct_answer: str
    option1: str
    option2: str
    option3: str
    audio: str


class LessonData(TypedDict):
    """Типизированный словарь для хранения данных об уроке."""

    lesson: Lesson
    is_completed: bool
    score: int


class LevelData(TypedDict):
    """Типизированный словарь для хранения данных об уровне языка."""

    level: LanguageLevel
    is_unlocked: bool
    is_completed: bool


def main_page(request: WSGIRequest) -> HttpResponse:
    """Отображение главной страницы."""
    return render(request, 'html/pages/main_page.html')


def policy_view(request: WSGIRequest) -> HttpResponse:
    """Отображение страницы с политикой конфиденциальности."""
    return render(request, 'html/pages/policy_page.html')


def login_view(request: WSGIRequest) -> Union[HttpResponse, HttpResponseRedirect]:
    """
    Обработка входа пользователя.

    Если метод POST - аутентифицирует пользователя.
    Если метод GET - отображает форму входа.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('main_page')
        messages.error(request, 'Invalid username or password')

    form = UserLogInForm(request.POST if request.method == 'POST' else None)
    return render(request, 'html/pages/login_page.html', {'form': form})


def register_view(request: WSGIRequest) -> Union[HttpResponse, HttpResponseRedirect]:
    """
    Обработка регистрации нового пользователя.

    Если метод POST и форма валидна - создает нового пользователя.
    Если метод GET - отображает форму регистрации.
    """
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
def tasks_view(
    request: WSGIRequest, level: LanguageLevelType, lesson: int
) -> Union[HttpResponse, HttpResponseRedirect]:
    """
    Отображение и обработка заданий урока.

    Args:
        request: Запрос WSGI
        level: Уровень языка (A1, A2 и т.д.)
        lesson: Номер урока

    Returns:
        Если пользователь уже прошел урок на 100% - редирект на страницу уроков
        Если метод POST - проверяет ответы и сохраняет прогресс
        Если метод GET - отображает задания урока
    """
    # Проверяем, есть ли у пользователя прогресс по этому уроку с результатом 100%
    progress = UserTasksProgress.objects.filter(
        user=request.user, level=level.upper(), lesson=lesson, result=100
    ).first()

    if progress:
        messages.warning(request, 'You have already passed this lesson 100%!!')
        return redirect('lessons', level=level)

    # Получаем объекты уровня языка и урока
    language_level = get_object_or_404(LanguageLevel, level=level.upper())
    lesson_obj = get_object_or_404(Lesson, language_level=language_level, lesson_number=lesson)
    tasks = list(Task.objects.filter(lesson=lesson_obj).order_by('id'))

    if request.method == 'POST':
        # Дополнительная проверка на случай, если пользователь обойдет предупреждение
        if UserTasksProgress.objects.filter(user=request.user, level=level.upper(), lesson=lesson, result=100).exists():
            messages.warning(request, 'You have already completed this lesson!')
            return redirect('lessons', level=level)

        task_results: List[TaskResult] = []
        correct_count = 0

        # Проверяем ответы для каждого задания
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

        # Рассчитываем процент правильных ответов
        score = int((correct_count / len(tasks)) * 100) if tasks else 0

        # Если результат >= 70%, проверяем, нужно ли открыть следующий уровень
        if score >= 70:
            current_level = language_level.level
            level_order: List[LanguageLevelType] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
            if current_level in level_order:
                index = level_order.index(current_level)
                if index < len(level_order) - 1:
                    next_level = level_order[index + 1]
                    if not UserTasksProgress.objects.filter(user=request.user, level=next_level).exists():
                        messages.info(request, f'Congratulations! Level {next_level} is open to you!')

        # Сохраняем или обновляем прогресс пользователя
        UserTasksProgress.objects.update_or_create(
            user=request.user, level=level.upper(), lesson=lesson, defaults={'result': score}
        )

        context: Dict[str, Any] = {
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
def profile_view(request: WSGIRequest) -> HttpResponse:
    """Отображение профиля пользователя с его прогрессом."""
    unlocked_levels = request.user.profile.get_unlocked_levels()
    profile, _ = Profile.objects.get_or_create(user=request.user)
    task_progress = UserTasksProgress.objects.filter(user=request.user)

    return render(
        request,
        'html/pages/account_page.html',
        {
            'user': request.user,
            'profile': profile,
            'task_progress': task_progress,
            'language_level': unlocked_levels[-1] if unlocked_levels else None,
        },
    )


@login_required
def langlevel_view(request: WSGIRequest) -> HttpResponse:
    """Отображение списка уровней языка с информацией о доступности."""
    unlocked_levels = request.user.profile.get_unlocked_levels()
    all_levels = LanguageLevel.objects.all().order_by('level')

    levels_data: List[LevelData] = []
    for level in all_levels:
        levels_data.append(
            {
                'level': level,
                'is_unlocked': level.level in unlocked_levels,
                'is_completed': check_level_completion(request.user, level.level),
            }
        )

    return render(request, 'html/pages/langlevel_page.html', {'levels_data': levels_data})


def check_level_completion(user: User, level: str) -> bool:
    """
    Проверяет, полностью ли завершен уровень пользователем.

    Args:
        user: Пользователь
        level: Уровень языка для проверки

    Returns:
        True если все уроки уровня завершены на 100%, иначе False
    """
    lessons = Lesson.objects.filter(language_level__level=level)
    for lesson in lessons:
        progress = UserTasksProgress.objects.filter(user=user, level=level, lesson=lesson.lesson_number).first()
        if not progress or progress.result < 100:
            return False
    return True


@login_required
def lessons_view(request: WSGIRequest, level: str) -> HttpResponse:
    """
    Отображение списка уроков для указанного уровня.

    Args:
        request: Запрос WSGI
        level: Уровень языка

    Returns:
        Страница с списком уроков и информацией о прогрессе
    """
    lessons: QuerySet[Lesson] = Lesson.objects.filter(language_level__level=level.upper()).order_by('lesson_number')

    user_progress = UserTasksProgress.objects.filter(user=request.user, level=level.upper())

    lessons_data: List[LessonData] = []
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
def edit_profile(request: WSGIRequest) -> Union[HttpResponse, HttpResponseRedirect]:
    """
    Редактирование профиля пользователя.

    Обрабатывает три формы:
    - Изменение аватара профиля
    - Изменение email
    - Изменение пароля

    Returns:
        Если форма отправлена и валидна - редирект на страницу редактирования
        Иначе - отображение формы редактирования
    """
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
            update_session_auth_hash(request, user)
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
