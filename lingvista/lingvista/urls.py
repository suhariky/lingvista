from django.contrib import admin
from django.urls import path
from lingvista_web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('profile/', views.profile_view, name='profile'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    path('dictionary/', views.dictionary_view, name='dictionary'),
    path('login_page/', views.login_view, name='login'),
    path('registry_page/', views.register_view, name='register'),
    path('langlevel_page/', views.langlevel_view, name='langlevel'),
    path('account_page/', views.profile_view, name='profile'),
]
