from django.contrib import admin
from django.urls import path
from lingvista_web.views import index, login_view, register_view, tasks_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('tasks/', tasks_view, name='tasks'),
]
