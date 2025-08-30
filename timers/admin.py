from django.contrib import admin
from .models import Clock, Stage, UserProfile

admin.site.register(Clock)
admin.site.register(Stage)
admin.site.register(UserProfile)
