from django.contrib import admin
from django.urls import path
from lingvista_web import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.main_page, name='main_page'),
    path('login_page/', views.login_view, name='login'),
    path('registry_page/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main_page'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('langlevel_page/', views.langlevel_view, name='langlevel'),
    path('account_page/', views.profile, name='profile'),
    path('accountedit_page/', views.edit_profile, name='edit_profile'),
    path('<str:level>_lessons_page/', views.lessons_view, name='lessons'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/history/', views.profile_history, name='profile_history'),
]
