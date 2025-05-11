# Маршруты URL (urls.py)

В этом разделе описаны все URL-маршруты Django-проекта Lingvista.

---

## Основные маршруты

### Главная страница
- **URL**: `/`
- **View**: `views.main_page`
- **Имя**: `main_page`
- **Описание**: Отображает главную страницу приложения.

### Административная панель
- **URL**: `/admin/`
- **View**: `admin.site.urls`
- **Описание**: Стандартная админ-панель Django.

---

## Аутентификация

### Вход
- **URL**: `/login_page/`
- **View**: `views.login_view`
- **Имя**: `login`
- **Описание**: Страница входа в систему.

### Регистрация
- **URL**: `/registry_page/`
- **View**: `views.register_view`
- **Имя**: `register`
- **Описание**: Страница регистрации новых пользователей.

### Выход
- **URL**: `/logout/`
- **View**: `auth_views.LogoutView`
- **Имя**: `logout`
- **Перенаправление**: На главную страницу (`main_page`)

---

## Восстановление пароля

### Запрос сброса
- **URL**: `/password_reset/`
- **View**: `auth_views.PasswordResetView`
- **Шаблон**: `html/pages/password_reset_form.html`
- **Имя**: `password_reset`

### Подтверждение отправки
- **URL**: `/password_reset/done/`
- **View**: `auth_views.PasswordResetDoneView`
- **Шаблон**: `html/pages/password_reset_done.html`
- **Имя**: `password_reset_done`

### Подтверждение сброса
- **URL**: `/reset/<uidb64>/<token>/`
- **View**: `auth_views.PasswordResetConfirmView`
- **Шаблон**: `html/pages/password_reset_confirm.html`
- **Имя**: `password_reset_confirm`

### Завершение сброса
- **URL**: `/reset/done/`
- **View**: `auth_views.PasswordResetCompleteView`
- **Шаблон**: `html/pages/password_reset_complete.html`
- **Имя**: `password_reset_complete`

---

## Учебные материалы

### Уровни языка
- **URL**: `/langlevel_page/`
- **View**: `views.langlevel_view`
- **Имя**: `langlevel`
- **Описание**: Отображает доступные уровни языка.

### Уроки уровня
- **URL**: `/<str:level>_lessons_page/`
- **View**: `views.lessons_view`
- **Имя**: `lessons`
- **Описание**: Список уроков для конкретного уровня.

### Задания урока
- **URL**: `/tasks_<str:level>_lesson<str:lesson>/`
- **View**: `views.tasks_view`
- **Имя**: `tasks`
- **Описание**: Задания для конкретного урока.

---

## Профиль пользователя

### Просмотр профиля
- **URL**: `/account_page/`
- **View**: `views.profile_view`
- **Имя**: `profile_view`
- **Описание**: Страница профиля пользователя.

### Редактирование профиля
- **URL**: `/accountedit_page/`
- **View**: `views.edit_profile`
- **Имя**: `edit_profile`
- **Описание**: Страница редактирования профиля.

---

## Прочие маршруты

### Политика конфиденциальности
- **URL**: `/policy/`
- **View**: `views.policy_view`
- **Имя**: `private_policy`
- **Описание**: Страница с политикой конфиденциальности.

---

## Медиа файлы

Маршруты для обслуживания медиафайлов в режиме разработки:
```python
static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Схема URL-маршрутов

| URL-путь                          | Назначение                          | Имя маршрута (name)       |
|-----------------------------------|-------------------------------------|---------------------------|
| `/`                               | Главная страница                    | `main_page`               |
| `/admin/`                         | Админ-панель                        | -                         |
| `/login_page/`                    | Страница входа                      | `login`                   |
| `/registry_page/`                 | Страница регистрации                | `register`                |
| `/logout/`                        | Выход из системы                    | `logout`                  |
| `/password_reset/`                | Запрос сброса пароля                | `password_reset`          |
| `/password_reset/done/`           | Подтверждение отправки              | `password_reset_done`     |
| `/reset/<uidb64>/<token>/`        | Подтверждение сброса                | `password_reset_confirm`  |
| `/reset/done/`                    | Завершение сброса                   | `password_reset_complete` |
| `/langlevel_page/`                | Список уровней языка                | `langlevel`               |
| `/<level>_lessons_page/`          | Уроки конкретного уровня            | `lessons`                 |
| `/tasks_<level>_lesson<lesson>/`  | Задания урока                       | `tasks`                   |
| `/account_page/`                  | Профиль пользователя                | `profile_view`            |
| `/accountedit_page/`              | Редактирование профиля              | `edit_profile`            |
| `/policy/`                        | Политика конфиденциальности         | `private_policy`          |

Все URL-адреса имеют соответствующие имена (`name`), которые используются для генерации ссылок в шаблонах.
 
