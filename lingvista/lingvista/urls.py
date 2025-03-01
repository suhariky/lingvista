from django.contrib import admin
from django.urls import path
from lingvista_web.views import index, login_view, register_view, tasks_view, profile_view, leaderboard_view, dictionary_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('tasks/', tasks_view, name='tasks'),
    path('profile/', profile_view, name='profile'),
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    path('dictionary/', dictionary_view, name='dictionary'),
]
