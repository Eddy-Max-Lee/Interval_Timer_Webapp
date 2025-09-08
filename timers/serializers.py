
from rest_framework import serializers
from .models import Clock, Stage

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id','order_index','name','duration_sec','tts_enabled','speak_every_sec','countdown_speak_from_sec','cue_beep_last_n_sec','voice_volume','voice_rate','voice_pitch','bgm_volume_override']

class ClockSerializer(serializers.ModelSerializer):
    stages = StageSerializer(many=True)
    class Meta:
        model = Clock
        fields = ['id','name','repeat_count','is_public','bgm_url','stages']

    def create(self, validated_data):
        stages_data = validated_data.pop('stages', [])
        request = self.context['request']
        owner = request.COOKIES.get('owner_token', 'anonymous')
        clock = Clock.objects.create(owner_token=owner, **validated_data)

        for i, s in enumerate(stages_data, start=1):
            s = dict(s)                 # 避免直接改到原物件
            s.pop('order_index', None)  # 移除，避免和下一行衝突
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
                s = dict(s)  # 複製一份
                s.pop('order_index', None)  # 移除 dict 中的 order_index，避免衝突
                Stage.objects.create(clock=instance, order_index=i, **s)
        return instance
