import logging

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)


class Audio(models.Model):
    """
    Модель для хранения аудиофайлов и ссылок на аудио.

    Attributes:
        title (CharField): Название аудио (необязательное).
        audio_file (FileField): Поле для загрузки аудиофайла (необязательное).
        audio_url (URLField): Ссылка на аудио (необязательное).
        description (TextField): Описание аудио (необязательное).
    """

    title = models.CharField(max_length=255, blank=True, null=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    audio_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.title) or "Audio"

    def save(self, *args, **kwargs):
        try:
            created = not self.pk
            super().save(*args, **kwargs)
            if created:
                logger.info(f"Created new Audio: {self.title or 'Untitled'}")
            else:
                logger.debug(f"Updated Audio: {self.title or 'Untitled'}")
        except Exception as e:
            logger.error(f"Error saving Audio: {str(e)}", exc_info=True)
            raise


class Profile(models.Model):
    """
    Модель профиля пользователя, расширяющая стандартную модель User.

    Attributes:
        user (OneToOneField): Связь один-к-одному с моделью User.
        profile_photo (ImageField): Фото профиля (необязательное).
        streak (IntegerField): Текущая серия дней активности (по умолчанию 0).
        completed_levels (IntegerField): Количество пройденных уровней (по умолчанию 0).
        language_level (CharField): Текущий уровень языка пользователя.
        achievements (TextField): Достижения пользователя (необязательное).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    streak = models.IntegerField(default=0)
    completed_levels = models.IntegerField(default=0)
    language_level = models.CharField(max_length=50, blank=True)
    achievements = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        try:
            created = not self.pk
            super().save(*args, **kwargs)
            if created:
                logger.info(f"Created new Profile for user: {self.user.username}")
            else:
                logger.debug(f"Updated Profile for user: {self.user.username}")
        except Exception as e:
            logger.error(f"Error saving Profile for user {self.user.username}: {str(e)}", exc_info=True)
            raise

    def get_unlocked_levels(self):
        """
        Возвращает список доступных пользователю уровней на основе прогресса.

        Returns:
            list: Список доступных уровней (например, ['A1', 'A2']).
        """
        logger.debug(f"Getting unlocked levels for user: {self.user.username}")
        try:
            levels = ['A1']
            level_order = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

            for i in range(len(level_order) - 1):
                current_level = level_order[i]
                next_level = level_order[i + 1]

                lessons = Lesson.objects.filter(language_level__level=current_level)
                completed = True

                for lesson in lessons:
                    progress = UserTasksProgress.objects.filter(
                        user=self.user, level=current_level, lesson=lesson.lesson_number
                    ).first()

                    if not progress or progress.result < 70:
                        completed = False
                        break

                if completed and next_level not in levels:
                    logger.info(f"User {self.user.username} unlocked new level: {next_level}")
                    levels.append(next_level)

            logger.debug(f"Unlocked levels for user {self.user.username}: {levels}")
            return levels
        except Exception as e:
            logger.error(f"Error in get_unlocked_levels for user {self.user.username}: {str(e)}", exc_info=True)
            raise

    def increment_streak(self):
        """Увеличивает счетчик дней активности пользователя на 1."""
        try:
            self.streak += 1
            self.save()
            logger.info(f"User {self.user.username} streak increased to {self.streak}")
        except Exception as e:
            logger.error(f"Error incrementing streak for user {self.user.username}: {str(e)}", exc_info=True)
            raise

    def reset_streak(self):
        """Сбрасывает счетчик дней активности пользователя в 0."""
        try:
            logger.info(f"User {self.user.username} streak reset from {self.streak} to 0")
            self.streak = 0
            self.save()
        except Exception as e:
            logger.error(f"Error resetting streak for user {self.user.username}: {str(e)}", exc_info=True)
            raise

    def complete_level(self):
        """Увеличивает счетчик пройденных уровней на 1."""
        try:
            logger.info(f"User {self.user.username} completed level, total now: {self.completed_levels + 1}")
            self.completed_levels += 1
            self.save()
        except Exception as e:
            logger.error(f"Error completing level for user {self.user.username}: {str(e)}", exc_info=True)
            raise

    def add_achievement(self, achievement):
        """
        Добавляет новое достижение в профиль пользователя.

        Args:
            achievement (str): Текст достижения для добавления.
        """
        try:
            logger.info(f"Adding achievement to user {self.user.username}: {achievement}")
            if self.achievements:
                self.achievements += f", {achievement}"
            else:
                self.achievements = achievement
            self.save()
        except Exception as e:
            logger.error(f"Error adding achievement for user {self.user.username}: {str(e)}", exc_info=True)
            raise


class LanguageLevel(models.Model):
    """
    Модель уровней владения языком (A1-C2).

    Attributes:
        level (CharField): Уровень языка (выбор из LEVEL_CHOICES).
        description (TextField): Описание уровня (необязательное).
    """

    LEVEL_CHOICES = [
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C1', 'C1'),
        ('C2', 'C2'),
    ]

    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.level)

    def save(self, *args, **kwargs):
        try:
            created = not self.pk
            super().save(*args, **kwargs)
            if created:
                logger.info(f"Created new LanguageLevel: {self.level}")
            else:
                logger.debug(f"Updated LanguageLevel: {self.level}")
        except Exception as e:
            logger.error(f"Error saving LanguageLevel {self.level}: {str(e)}", exc_info=True)
            raise


class Lesson(models.Model):
    """
    Модель урока, привязанного к определенному уровню языка.

    Attributes:
        language_level (ForeignKey): Связь с уровнем языка.
        lesson_number (IntegerField): Номер урока в рамках уровня.
        title (CharField): Название урока.
        description (TextField): Описание урока (необязательное).
    """

    language_level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE, related_name='lessons')
    lesson_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.language_level.level} - Lesson {self.lesson_number}: {self.title}"

    def save(self, *args, **kwargs):
        try:
            created = not self.pk
            super().save(*args, **kwargs)
            if created:
                logger.info(f"Created new Lesson: {self.title} for level {self.language_level.level}")
            else:
                logger.debug(f"Updated Lesson: {self.title} for level {self.language_level.level}")
        except Exception as e:
            logger.error(f"Error saving Lesson {self.title}: {str(e)}", exc_info=True)
            raise


class Task(models.Model):
    """
    Модель задания для урока.

    Attributes:
        lesson (ForeignKey): Связь с уроком.
        question (TextField): Текст вопроса.
        correct_answer (CharField): Правильный ответ.
        option1-3 (CharField): Варианты ответов (необязательные).
        audio (ForeignKey): Связь с аудио для задания (необязательная).
    """

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question = models.TextField()
    correct_answer = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255, blank=True, null=True)
    option2 = models.CharField(max_length=255, blank=True, null=True)
    option3 = models.CharField(max_length=255, blank=True, null=True)
    audio = models.ForeignKey(Audio, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Task for {self.lesson.title}"

    def save(self, *args, **kwargs):
        try:
            created = not self.pk
            super().save(*args, **kwargs)
            if created:
                logger.info(f"Created new Task for lesson {self.lesson.title}")
            else:
                logger.debug(f"Updated Task for lesson {self.lesson.title}")
        except Exception as e:
            logger.error(f"Error saving Task for lesson {self.lesson.title}: {str(e)}", exc_info=True)
            raise


class UserTasksProgress(models.Model):
    """
    Модель для отслеживания прогресса пользователя по заданиям.

    Attributes:
        user (ForeignKey): Связь с пользователем.
        level (CharField): Уровень языка (по умолчанию 'A1').
        lesson (IntegerField): Номер урока (по умолчанию 1).
        result (IntegerField): Результат в процентах (по умолчанию 0).
        date_completed (DateTimeField): Дата завершения (автоматически при создании).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=2, default='A1')
    lesson = models.IntegerField(default=1)
    result = models.IntegerField(default=0)
    date_completed = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'level', 'lesson')

    def __str__(self):
        return f"{self.user.username} - Level {self.level} - Lesson {self.lesson} - Result {self.result}%"

    def save(self, *args, **kwargs):
        try:
            created = not self.pk
            super().save(*args, **kwargs)
            if created:
                logger.info(
                    f"New progress record: "
                    f"{self.user.username} - Level {self.level} - Lesson {self.lesson} - {self.result}%"
                )
            else:
                logger.debug(
                    f"Updated progress: "
                    f"{self.user.username} - Level {self.level} - Lesson {self.lesson} - {self.result}%"
                )

            if self.result >= 70:
                logger.info(
                    f"User {self.user.username} successfully completed lesson {self.lesson} "
                    f"at level {self.level} with score {self.result}%"
                )
        except Exception as e:
            logger.error(f"Error saving UserTasksProgress for {self.user.username}: {str(e)}", exc_info=True)
            raise
