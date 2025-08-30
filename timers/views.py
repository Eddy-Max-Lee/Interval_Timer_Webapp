from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from rest_framework import generics, permissions
from .models import Clock
from .serializers import ClockSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model


def ping(request): return JsonResponse({'ping': 'pong'})

#@login_required
def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # 或 'index'，視你的設定而定
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
    
@method_decorator(csrf_exempt, name='dispatch')
class ClockListCreateView(generics.ListCreateAPIView):
    queryset = Clock.objects.all()
    serializer_class = ClockSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get("mine") == "1":
            if self.request.user.is_authenticated:
                qs = qs.filter(user=self.request.user)
            else:
                guest_user = get_user_model().objects.get(username='guest')
                qs = qs.filter(user=guest_user)
        elif self.request.GET.get("public") == "1":
            qs = qs.filter(is_public=True)
        return qs

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            # 自動指派給「訪客帳號」
            User = get_user_model()
            user = User.objects.get(username='guest')
        serializer.save(user=user)
