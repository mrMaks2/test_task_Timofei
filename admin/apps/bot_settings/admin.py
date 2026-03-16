from django.contrib import admin
from .models import Channel, Setting

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'title', 'is_mandatory']
    list_editable = ['is_mandatory']

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']