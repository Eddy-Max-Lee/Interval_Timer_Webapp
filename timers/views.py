from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from .models import Clock, Stage, UserProfile
from .serializers import ClockSerializer, StageSerializer, ProfileSerializer


class ClockViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ClockSerializer
    queryset = Clock.objects.select_related('user').prefetch_related('stages').order_by('-created_at')

    def get_queryset(self):
        qs = super().get_queryset()
        public = self.request.query_params.get('public')
        mine = self.request.query_params.get('mine')
        if public == '1':
            qs = qs.filter(is_public=True)
        elif mine == '1':
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def fork(self, request, pk=None):
        src = self.get_object()
        if Clock.objects.filter(user=request.user).count() >= 10:
            return Response({'detail': 'You already have 10 clocks.'}, status=400)
        data = ClockSerializer(src).data
        data['is_public'] = False
        serializer = ClockSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        new_clock = serializer.save()
        return Response(ClockSerializer(new_clock).data)


class StageViewSet(viewsets.ModelViewSet):
    serializer_class = StageSerializer
    queryset = Stage.objects.all()


class MeProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prof, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(ProfileSerializer(prof).data)

    def put(self, request):
        prof, _ = UserProfile.objects.get_or_create(user=request.user)
        ser = ProfileSerializer(prof, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)

