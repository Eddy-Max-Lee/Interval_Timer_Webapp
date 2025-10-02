from django.conf import settings
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from timers.utils import get_request_profile


@ensure_csrf_cookie
def home(request):
    if not get_request_profile(request):
        return redirect('login')
    return render(request, 'index.html')


@ensure_csrf_cookie
def login_view(request):
    if get_request_profile(request):
        return redirect('home')
    return render(request, 'login.html', {'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID})
