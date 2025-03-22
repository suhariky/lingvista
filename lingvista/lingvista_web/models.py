from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

class Audio(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)  # Название аудио
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)  # Файл аудио
    audio_url = models.URLField(blank=True, null=True)  # Ссылка на аудио
    description = models.TextField(blank=True, null=True)  # Описание (необязательно)

    def __str__(self):
        return self.title or "Audio"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    streak = models.IntegerField(default=0)
    completed_levels = models.IntegerField(default=0)
    language_level = models.CharField(max_length=50)
    achievements = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

    def increment_streak(self):
        self.streak += 1
        self.save()

    def reset_streak(self):
        self.streak = 0
        self.save()

    def complete_level(self):
        self.completed_levels += 1
        self.save()

    def add_achievement(self, achievement):
        if self.achievements:
            self.achievements += f", {achievement}"
        else:
            self.achievements = achievement
        self.save()


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=255, unique=True, blank=True, null=True)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Указываем уникальные related_name для groups и user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_groups",  # Уникальное имя для обратной ссылки
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_permissions",  # Уникальное имя для обратной ссылки
        related_query_name="customuser",
    )

    def __str__(self):
        return self.nickname if self.nickname else self.username

class LanguageLevel(models.Model):
    #список кортежей из значений, которые будут в БД и которые будут отображаться на странице
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
        return self.level

class Lesson(models.Model):
    language_level = models.ForeignKey(LanguageLevel, on_delete=models.CASCADE, related_name='lessons')
    lesson_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.language_level.level} - Lesson {self.lesson_number}: {self.title}"

class Task(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    question = models.TextField()
    correct_answer = models.CharField(max_length=255)
    option1 = models.CharField(max_length=255, blank=True, null=True)
    option2 = models.CharField(max_length=255, blank=True, null=True)
    option3 = models.CharField(max_length=255, blank=True, null=True)
    audio = models.ForeignKey(Audio, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"Task for {self.lesson.title}"

class UserProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='progress')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    date_completed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.lesson.title} - Task {self.task.id}"
