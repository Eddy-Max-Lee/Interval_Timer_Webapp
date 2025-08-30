
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('timers.urls')),
    path('auth/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/signup/', include('timers.auth_urls')),
    path('accounts/', include('allauth.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
]
