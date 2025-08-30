
from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tts_lang = models.CharField(max_length=16, default='zh-TW')
    tts_voice_hint = models.CharField(max_length=64, blank=True, default='')

    def __str__(self):
        return f"Profile({self.user.username})"

class Clock(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clocks')
    name = models.CharField(max_length=120)
    repeat_count = models.PositiveIntegerField(default=1)
    is_public = models.BooleanField(default=False)
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
    youtube_url = models.URLField(blank=True, null=True)
    youtube_start_sec = models.PositiveIntegerField(default=0)
    youtube_end_sec = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['order_index', 'id']

    def __str__(self):
        return f"{self.order_index}. {self.name or 'Stage'}"
