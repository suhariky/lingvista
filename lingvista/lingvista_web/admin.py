from django.contrib import admin
from .models import LanguageLevel, Lesson, Task, UserTasksProgress, Profile

admin.site.register(LanguageLevel)
admin.site.register(Lesson)
admin.site.register(Task)
admin.site.register(UserTasksProgress)
admin.site.register(Profile)
