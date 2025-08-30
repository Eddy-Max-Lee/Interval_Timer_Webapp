from django.urls import path
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def signup(request):
    if request.method == 'POST':
        u = request.POST['username']
        p = request.POST['password']
        if User.objects.filter(username=u).exists():
            return render(request, 'signup.html', {'error': '使用者已存在'})
        User.objects.create_user(username=u, password=p)
        return redirect('login')
    return render(request, 'signup.html')


urlpatterns = [
    path('', signup, name='signup'),
]

