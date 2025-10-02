
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClockViewSet,
    CurrentUserView,
    GuestLoginView,
    GoogleLoginView,
    LogoutView,
    StageViewSet,
)

router = DefaultRouter()
router.register(r'clocks', ClockViewSet, basename='clock')
router.register(r'stages', StageViewSet, basename='stage')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/me/', CurrentUserView.as_view(), name='auth-me'),
    path('auth/google/', GoogleLoginView.as_view(), name='auth-google'),
    path('auth/guest/', GuestLoginView.as_view(), name='auth-guest'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
]
