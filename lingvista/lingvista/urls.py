from django.contrib import admin
from django.urls import path
from lingvista_web.views import index, login_view, register_view, langlevel_view, profile_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login_page/', login_view, name='login'),
    path('registry_page/', register_view, name='register'),
    path('langlevel_page/', langlevel_view, name='langlevel'),
    path('account_page/', profile_view, name='profile'),
]
