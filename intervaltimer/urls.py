
from django.contrib import admin
from django.urls import path, include
from .views import home, login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('timers.urls')),
    path('', home, name='home'),
    path('login/', login_view, name='login'),
]
