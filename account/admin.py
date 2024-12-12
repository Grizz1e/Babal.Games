from django.contrib import admin
from .models import ProfileAvatar, UserProfile

# Register your models here.
@admin.register(ProfileAvatar)
class ProfileAvatarAdmin(admin.ModelAdmin):
    list_display = ['avatar', 'game']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar_id']