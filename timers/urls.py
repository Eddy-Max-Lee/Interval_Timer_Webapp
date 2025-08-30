from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('clocks/', views.ClockListCreateView.as_view(), name='clock-list-create'),

    # 內建帳號登入登出
    path('accounts/', include('django.contrib.auth.urls')),

    # 自訂註冊功能
    path('accounts/', include('timers.auth_urls')),

    # timers 應用的主要路由
    #path('timers/', include('timers.urls')),

    # 預設首頁導向登入畫面
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False)),
]
