
from rest_framework import serializers
from .models import Clock, Stage, UserProfile

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = [
            'id','order_index','name','duration_sec','tts_enabled','speak_every_sec',
            'countdown_speak_from_sec','cue_beep_last_n_sec','voice_volume','voice_rate',
            'voice_pitch','bgm_volume_override','youtube_url','youtube_start_sec','youtube_end_sec'
        ]

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['tts_lang','tts_voice_hint']

class ClockSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    stages = StageSerializer(many=True)

    class Meta:
        model = Clock
        fields = ['id','name','repeat_count','is_public','bgm_url','stages','author']

    def get_author(self, obj):
        return obj.user.username

    def create(self, validated_data):
        stages_data = validated_data.pop('stages', [])
        request = self.context['request']
        clock = Clock.objects.create(user=request.user, **validated_data)
        for i, s in enumerate(stages_data, start=1):
            Stage.objects.create(clock=clock, order_index=i, **s)
        return clock

    def update(self, instance, validated_data):
        stages_data = validated_data.pop('stages', None)
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
