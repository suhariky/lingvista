from django.shortcuts import render

def index(request):
    return render(request, 'html/pages/index.html')

def login_view(request):
    return render(request, 'html/pages/login_page.html')

def register_view(request):
    return render(request, 'html/pages/registry_page.html')

def tasks_view(request):
    return render(request, 'html/pages/tasks_page.html')
