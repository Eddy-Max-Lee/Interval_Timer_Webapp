
from django.contrib import admin
from .models import Clock, Stage, UserProfile

class StageInline(admin.TabularInline):
    model = Stage
    extra = 0

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'display_name',
        'email',
        'is_guest',
        'gender',
        'age',
        'height_cm',
        'weight_kg',
        'created_at',
    )
    search_fields = ('display_name', 'email')


@admin.register(Clock)
class ClockAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'repeat_count', 'is_public', 'owner', 'created_at')
    inlines = [StageInline]

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('id', 'clock', 'order_index', 'name', 'duration_sec')
