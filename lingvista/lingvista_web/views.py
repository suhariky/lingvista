from django.shortcuts import render

def index(request):
    return render(request, 'html/pages/index.html')

def login_view(request):
    return render(request, 'html/pages/login_page.html')

def register_view(request):
    return render(request, 'html/pages/registry_page.html')

def tasks_view(request):
    return render(request, 'html/pages/tasks_page.html')

def profile_view(request):
    return render(request, 'html/pages/account_page.html')

def leaderboard_view(request):
    return render(request, 'html/pages/leaderboard_page.html')

def dictionary_view(request):
    return render(request, 'html/pages/dictionary_page.html')

def langlevel_view(request):
    return render(request, 'html/pages/langlevel_page.html')
