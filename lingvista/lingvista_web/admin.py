from django.contrib import admin
from .models import LanguageLevel, Lesson, Task, UserProgress, Profile

admin.site.register(LanguageLevel)
admin.site.register(Lesson)
admin.site.register(Task)
admin.site.register(UserProgress)
admin.site.register(Profile)
