import logging
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

LanguageLevelType = Literal['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
logger = logging.getLogger(__name__)


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
    logger.debug(
        f"Main page accessed by "
        f"{'authenticated user ' + request.user.username if request.user.is_authenticated else 'anonymous user'}"
    )
    return render(request, 'html/pages/main_page.html')


def policy_view(request: WSGIRequest) -> HttpResponse:
    """Отображение страницы с политикой конфиденциальности."""
    logger.debug(
        f"Policy page accessed by "
        f"{'authenticated user ' + request.user.username if request.user.is_authenticated else 'anonymous user'}"
    )
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
        logger.debug(f"Attempting login for user: {username}")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            logger.info(f"User {username} logged in successfully")

            storage = messages.get_messages(request)
            for message in storage:
                pass
            storage.used = True

            return redirect('main_page')

        logger.warning(f"Failed login attempt for user: {username}")
        messages.error(request, 'Invalid username or password', extra_tags='login')

    all_messages = messages.get_messages(request)
    login_messages = []
    for message in all_messages:
        if 'login' in message.tags:
            login_messages.append(message)

    storage = messages.get_messages(request)
    storage.used = True

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
            logger.info(f"New user registered: {user.username}, email: {user.email}")
            messages.success(request, 'Registration is successful!')
            return redirect('main_page')
        logger.warning(f"Registration failed with errors: {form.errors}")
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

    logger.info(f"User {request.user.username} accessing tasks for level {level}, lesson {lesson}")
    progress = UserTasksProgress.objects.filter(
        user=request.user, level=level.upper(), lesson=lesson, result=100
    ).first()

    if progress:
        logger.debug(f"User {request.user.username} already completed lesson {lesson} at level {level}")
        messages.warning(request, 'You have already passed this lesson 100%!!')
        return redirect('lessons', level=level)

    language_level = get_object_or_404(LanguageLevel, level=level.upper())
    lesson_obj = get_object_or_404(Lesson, language_level=language_level, lesson_number=lesson)
    tasks = list(Task.objects.filter(lesson=lesson_obj).order_by('id'))

    if request.method == 'POST':

        if UserTasksProgress.objects.filter(user=request.user, level=level.upper(), lesson=lesson, result=100).exists():
            messages.warning(request, 'You have already completed this lesson!')
            return redirect('lessons', level=level)

        task_results: List[TaskResult] = []
        correct_count = 0

        for task in tasks:
            field, strategy = get_check_strategy(task)
            user_answer = request.POST.get(f'{field}_{task.id}', '').strip()
            is_correct = strategy.check_answer(task, user_answer)

            logger.debug(
                f"Task {task.id} answer check - user: {user_answer}, "
                f"correct: {task.correct_answer}, result: {is_correct}"
            )

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
        logger.info(f"User {request.user.username} completed lesson {lesson} at level {level} with score {score}%")

        if score >= 70:
            current_level = language_level.level
            level_order: List[LanguageLevelType] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
            if current_level in level_order:
                index = level_order.index(current_level)
                if index < len(level_order) - 1:
                    next_level = level_order[index + 1]
                    if not UserTasksProgress.objects.filter(user=request.user, level=next_level).exists():
                        logger.info(f"User {request.user.username} unlocked new level: {next_level}")
                        messages.info(request, f'Congratulations! Level {next_level} is open to you!')

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
    logger.info(f"User {request.user.username} accessing profile page")
    try:
        unlocked_levels = request.user.profile.get_unlocked_levels()
        profile, created = Profile.objects.get_or_create(user=request.user)
        if created:
            logger.info(f"Created new profile for user {request.user.username}")

        task_progress = UserTasksProgress.objects.filter(user=request.user)
        logger.debug(f"Found {task_progress.count()} progress records for user {request.user.username}")

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
    except Exception as e:
        logger.error(f"Error in profile_view for user {request.user.username}: {str(e)}", exc_info=True)
        raise


@login_required
def langlevel_view(request: WSGIRequest) -> HttpResponse:
    """Отображение списка уровней языка с информацией о доступности."""
    logger.info(f"User {request.user.username} accessing language levels page")
    try:
        unlocked_levels = request.user.profile.get_unlocked_levels()
        all_levels = LanguageLevel.objects.all().order_by('level')
        logger.debug(f"Found {all_levels.count()} language levels in system")

        levels_data: List[LevelData] = []
        for level in all_levels:
            is_completed = check_level_completion(request.user, level.level)
            levels_data.append(
                {
                    'level': level,
                    'is_unlocked': level.level in unlocked_levels,
                    'is_completed': is_completed,
                }
            )
            logger.debug(f"Level {level.level} - unlocked: {level.level in unlocked_levels}, completed: {is_completed}")

        return render(request, 'html/pages/langlevel_page.html', {'levels_data': levels_data})
    except Exception as e:
        logger.error(f"Error in langlevel_view for user {request.user.username}: {str(e)}", exc_info=True)
        raise


def check_level_completion(user: User, level: str) -> bool:
    """
    Проверяет, полностью ли завершен уровень пользователем.

    Args:
        user: Пользователь
        level: Уровень языка для проверки

    Returns:
        True если все уроки уровня завершены на 100%, иначе False
    """
    logger.debug(f"Checking level completion for user {user.username}, level {level}")
    try:
        lessons = Lesson.objects.filter(language_level__level=level)
        logger.debug(f"Found {lessons.count()} lessons for level {level}")

        for lesson in lessons:
            progress = UserTasksProgress.objects.filter(user=user, level=level, lesson=lesson.lesson_number).first()

            if not progress or progress.result < 100:
                logger.debug(
                    f"Lesson {lesson.lesson_number} not completed (progress: {progress.result if progress else 'none'})"
                )
                return False

        logger.debug(f"All lessons for level {level} completed")
        return True
    except Exception as e:
        logger.error(f"Error in check_level_completion for user {user.username}: {str(e)}", exc_info=True)
        raise


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
    logger.info(f"User {request.user.username} accessing lessons for level {level}")
    try:
        lessons: QuerySet[Lesson] = Lesson.objects.filter(language_level__level=level.upper()).order_by('lesson_number')
        user_progress = UserTasksProgress.objects.filter(user=request.user, level=level.upper())
        logger.debug(f"Found {lessons.count()} lessons and {user_progress.count()} progress records for level {level}")

        lessons_data: List[LessonData] = []
        for lesson in lessons:
            progress = user_progress.filter(lesson=lesson.lesson_number).first()
            is_completed = progress and progress.result == 100
            lessons_data.append(
                {'lesson': lesson, 'is_completed': is_completed, 'score': progress.result if progress else 0}
            )
            logger.debug(
                f"Lesson {lesson.lesson_number} - completed: {is_completed}, "
                f"score: {progress.result if progress else 0}"
            )

        context = {
            'level': level.upper(),
            'lessons_data': lessons_data,
        }
        return render(request, 'html/pages/lessons_page.html', context)
    except Exception as e:
        logger.error(f"Error in lessons_view for user {request.user.username}, level {level}: {str(e)}", exc_info=True)
        raise


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
    logger.info(f"User {request.user.username} accessing profile edit page")
    try:
        profile = request.user.profile

        if request.method == 'POST':
            profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
            email_form = EmailChangeForm(request.POST)
            password_form = CustomPasswordChangeForm(request.user, request.POST)

            if 'profile_submit' in request.POST and profile_form.is_valid():
                profile_form.save()
                logger.info(f"User {request.user.username} updated profile picture")
                messages.success(request, 'Your profile picture has been updated!')
                return redirect('edit_profile')

            if 'email_submit' in request.POST and email_form.is_valid():
                new_email = email_form.cleaned_data['email']
                request.user.email = new_email
                request.user.save()
                logger.info(f"User {request.user.username} changed email to {new_email}")
                messages.success(request, 'Your email has been updated!')
                return redirect('edit_profile')

            if 'password_submit' in request.POST and password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                logger.info(f"User {request.user.username} changed password")
                messages.success(request, 'Your password has been updated!')
                return redirect('edit_profile')

            logger.warning(
                f"Profile edit form errors for user {request.user.username}: "
                f"profile: {profile_form.errors}, email: {email_form.errors}, password: {password_form.errors}"
            )
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
    except Exception as e:
        logger.error(f"Error in edit_profile for user {request.user.username}: {str(e)}", exc_info=True)
        raise
