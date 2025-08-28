
from django.db import models

class Clock(models.Model):
    name = models.CharField(max_length=120)
    repeat_count = models.PositiveIntegerField(default=1)
    is_public = models.BooleanField(default=False)
    owner_token = models.CharField(max_length=64, db_index=True)
    bgm_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Stage(models.Model):
    clock = models.ForeignKey(Clock, related_name='stages', on_delete=models.CASCADE)
    order_index = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=120, blank=True, default='')
    duration_sec = models.PositiveIntegerField(default=10)
    tts_enabled = models.BooleanField(default=True)
    speak_every_sec = models.PositiveIntegerField(default=0)  # 0 = off
    countdown_speak_from_sec = models.PositiveIntegerField(default=0)
    cue_beep_last_n_sec = models.PositiveIntegerField(default=0)
    voice_volume = models.FloatField(default=1.0)
    voice_rate = models.FloatField(default=1.0)
    voice_pitch = models.FloatField(default=1.0)
    bgm_volume_override = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['order_index', 'id']

    def __str__(self):
        return f"{self.order_index}. {self.name or 'Stage'}"
