from django.contrib import admin
from django.urls import path
from lingvista_web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_page, name='main_page'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('login_page/', views.login_view, name='login'),
    path('registry_page/', views.register_view, name='register'),
    path('langlevel_page/', views.langlevel_view, name='langlevel'),
    path('account_page/', views.profile_view, name='profile'),
    path('accountedit_page/', views.accountedit_view, name='accountedit'),
    path('<str:level>_lessons_page/', views.lessons_view, name='lessons'),
]
