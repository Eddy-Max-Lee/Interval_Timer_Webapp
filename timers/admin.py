
from django.contrib import admin
from .models import Clock, Stage

class StageInline(admin.TabularInline):
    model = Stage
    extra = 0

@admin.register(Clock)
class ClockAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'repeat_count', 'is_public', 'owner_token', 'created_at')
    inlines = [StageInline]

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('id', 'clock', 'order_index', 'name', 'duration_sec')
