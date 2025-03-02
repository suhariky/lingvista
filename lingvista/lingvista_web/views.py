from django.shortcuts import render

def main_page(request):
    return render(request, 'html/pages/main_page.html')

def login_view(request):
    return render(request, 'html/pages/login_page.html')

def register_view(request):
    return render(request, 'html/pages/registry_page.html')

def tasks_view(request):
    return render(request, 'html/pages/tasks_page.html')

def profile_view(request):
    return render(request, 'html/pages/account_page.html')

def langlevel_view(request):
    return render(request, 'html/pages/langlevel_page.html')

def accountedit_view(request):
    return render(request, 'html/pages/accountedit_page.html')

def lessons_view(request, level):
    context = {
        'level': level.upper(),
    }
    return render(request, 'html/pages/lessons_page.html', context)

