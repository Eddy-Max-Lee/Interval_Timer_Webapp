import json
import logging
from urllib import error as urllib_error, request as urllib_request

from django.conf import settings
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

try:  # pragma: no cover - optional dependency
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token
except ImportError:  # pragma: no cover - fallback path
    google_requests = None
    id_token = None

from .models import Clock, Stage, UserProfile
from .serializers import ClockSerializer, StageSerializer, UserProfileSerializer
from .utils import get_request_profile


logger = logging.getLogger(__name__)


class CurrentUserView(APIView):
    def get(self, request):
        profile = get_request_profile(request)
        if not profile:
            return Response({'detail': '未登入'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(UserProfileSerializer(profile).data)

    def patch(self, request):
        profile = get_request_profile(request)
        if not profile:
            raise NotAuthenticated('未登入')

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def _verify_credential(self, credential: str, client_id: str):
        if id_token and google_requests:
            return id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                client_id,
            )

        token_info_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={credential}'
        try:
            with urllib_request.urlopen(token_info_url) as resp:  # nosec: B310 - Google endpoint
                payload = json.load(resp)
        except urllib_error.URLError as exc:
            raise ValueError('Google 驗證失敗') from exc

        if payload.get('aud') != client_id:
            raise ValueError('Google 驗證失敗')
        return payload

    def post(self, request):
        credential = request.data.get('credential')
        client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')

        if not credential:
            return Response({'detail': '缺少 Google Credential'}, status=status.HTTP_400_BAD_REQUEST)
        if not client_id:
            return Response({'detail': '尚未設定 GOOGLE_CLIENT_ID'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            id_info = self._verify_credential(credential, client_id)
        except ValueError as exc:  # pragma: no cover - depends on external call
            logger.warning('Google login failed: %s', exc)
            return Response({'detail': 'Google 驗證失敗'}, status=status.HTTP_400_BAD_REQUEST)

        sub = id_info.get('sub')
        email = id_info.get('email')
        name = id_info.get('name') or ''

        if not sub:
            return Response({'detail': 'Google 回傳資料異常'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            profile, _ = UserProfile.objects.get_or_create(
                google_sub=sub,
                defaults={'email': email, 'display_name': name, 'is_guest': False},
            )
            profile.email = email or profile.email
            profile.display_name = profile.display_name or name or ''
            profile.is_guest = False
            profile.save(update_fields=['email', 'display_name', 'is_guest', 'updated_at'])

        request.session['profile_id'] = str(profile.id)
        return Response(UserProfileSerializer(profile).data)


class GuestLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        display_name = request.data.get('display_name') or '訪客'
        with transaction.atomic():
            profile = UserProfile.objects.create(
                display_name=display_name,
                is_guest=True,
            )
        request.session['profile_id'] = str(profile.id)
        return Response(UserProfileSerializer(profile).data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    def post(self, request):
        request.session.flush()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClockViewSet(viewsets.ModelViewSet):
    serializer_class = ClockSerializer
    queryset = Clock.objects.all().select_related('owner').prefetch_related('stages').order_by('-created_at')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()
        public = self.request.query_params.get('public')
        mine = self.request.query_params.get('mine')
        profile = get_request_profile(self.request)

        if public == '1':
            qs = qs.filter(is_public=True)
        elif mine == '1':
            if not profile:
                return Clock.objects.none()
            qs = qs.filter(owner=profile)
        else:
            qs = qs.filter(is_public=True)
        return qs

    def _require_profile(self):
        profile = get_request_profile(self.request)
        if not profile:
            raise NotAuthenticated('請先登入')
        return profile

    def perform_create(self, serializer):
        profile = self._require_profile()
        instance = serializer.save()
        if instance.owner_id != profile.id:
            instance.owner = profile
            instance.save(update_fields=['owner'])
        if profile.is_guest and not instance.is_public:
            instance.is_public = True
            instance.save(update_fields=['is_public'])
        return instance

    def perform_update(self, serializer):
        profile = self._require_profile()
        clock = serializer.instance
        if clock.owner_id != profile.id:
            raise PermissionDenied('無法編輯其他人的時鐘')
        instance = serializer.save()
        if profile.is_guest and not instance.is_public:
            instance.is_public = True
            instance.save(update_fields=['is_public'])
        return instance

    def perform_destroy(self, instance):
        profile = self._require_profile()
        if instance.owner_id != profile.id:
            raise PermissionDenied('無法刪除其他人的時鐘')
        instance.delete()

    @action(detail=True, methods=['post'])
    def fork(self, request, pk=None):
        profile = self._require_profile()
        src = self.get_object()

        if Clock.objects.filter(owner=profile).count() >= 10:
            return Response({'detail': 'You already have 10 clocks.'}, status=status.HTTP_400_BAD_REQUEST)

        data = ClockSerializer(src, context={'request': request}).data
        if profile.is_guest:
            data['is_public'] = True
        else:
            data['is_public'] = False

        serializer = ClockSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        new_clock = serializer.save()
        new_clock.owner = profile
        if profile.is_guest:
            new_clock.is_public = True
        new_clock.save(update_fields=['owner', 'is_public'])
        return Response(ClockSerializer(new_clock, context={'request': request}).data)


class StageViewSet(viewsets.ModelViewSet):
    serializer_class = StageSerializer
    queryset = Stage.objects.all()
