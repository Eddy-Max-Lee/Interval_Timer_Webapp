
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Clock, Stage
from .serializers import ClockSerializer, StageSerializer

class ClockViewSet(viewsets.ModelViewSet):
    serializer_class = ClockSerializer
    queryset = Clock.objects.all().order_by('-created_at')

    def get_queryset(self):
        qs = super().get_queryset()
        owner = self.request.COOKIES.get('owner_token', '')
        public = self.request.query_params.get('public')
        mine = self.request.query_params.get('mine')
        if public == '1':
            qs = qs.filter(is_public=True)
        elif mine == '1':
            qs = qs.filter(owner_token=owner)
        return qs

    def perform_create(self, serializer):
        return serializer.save()

    @action(detail=True, methods=['post'])
    def fork(self, request, pk=None):
        owner = request.COOKIES.get('owner_token', '')
        src = self.get_object()
        # Enforce 10 clocks limit per owner
        if Clock.objects.filter(owner_token=owner).count() >= 10:
            return Response({'detail':'You already have 10 clocks.'}, status=400)
        data = ClockSerializer(src).data
        data['is_public'] = False
        serializer = ClockSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        new_clock = serializer.save()
        new_clock.owner_token = owner
        new_clock.save()
        return Response(ClockSerializer(new_clock).data)

class StageViewSet(viewsets.ModelViewSet):
    serializer_class = StageSerializer
    queryset = Stage.objects.all()
