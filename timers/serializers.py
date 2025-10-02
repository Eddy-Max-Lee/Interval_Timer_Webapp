from rest_framework import serializers

from .models import Clock, Stage, UserProfile
from .utils import get_request_profile


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = [
            'id',
            'order_index',
            'name',
            'duration_sec',
            'tts_enabled',
            'speak_every_sec',
            'countdown_speak_from_sec',
            'cue_beep_last_n_sec',
            'voice_volume',
            'voice_rate',
            'voice_pitch',
            'bgm_volume_override',
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'display_name',
            'email',
            'gender',
            'age',
            'height_cm',
            'weight_kg',
            'is_guest',
        ]
        read_only_fields = ['id', 'email', 'is_guest']


class ClockSerializer(serializers.ModelSerializer):
    stages = StageSerializer(many=True)

    class Meta:
        model = Clock
        fields = ['id', 'name', 'repeat_count', 'is_public', 'bgm_url', 'stages']

    def create(self, validated_data):
        stages_data = validated_data.pop('stages', [])
        request = self.context['request']
        profile = get_request_profile(request)
        if not profile:
            raise serializers.ValidationError('必須登入後才能建立時鐘')

        if profile.is_guest:
            if not validated_data.get('is_public', False):
                raise serializers.ValidationError({'is_public': '訪客帳號僅能建立公開時鐘'})
            validated_data['is_public'] = True

        clock = Clock.objects.create(owner=profile, **validated_data)

        for i, s in enumerate(stages_data, start=1):
            s = dict(s)  # 避免直接改到原物件
            s.pop('order_index', None)
            Stage.objects.create(clock=clock, order_index=i, **s)

        return clock

    def update(self, instance, validated_data):
        stages_data = validated_data.pop('stages', None)
        request = self.context['request']
        profile = get_request_profile(request)

        if profile and profile.is_guest and validated_data.get('is_public') is False:
            raise serializers.ValidationError({'is_public': '訪客帳號無法建立私人時鐘'})

        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()

        if stages_data is not None:
            instance.stages.all().delete()
            for i, s in enumerate(stages_data, start=1):
                s = dict(s)
                s.pop('order_index', None)
                Stage.objects.create(clock=instance, order_index=i, **s)
        return instance
