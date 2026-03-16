from django.contrib import admin
from .models import Mailing, MailingLog
import requests
from django.conf import settings

def send_mailing(modeladmin, request, queryset):
    for mailing in queryset.filter(status='ready'):
        # Отправка через бот
        response = requests.post(
            settings.BOT_WEBHOOK_URL,
            json={'event': 'start_mailing', 'mailing_id': mailing.id},
            headers={'Authorization': f'Bearer {settings.BOT_INTERNAL_TOKEN}'}
        )
        if response.status_code == 200:
            mailing.status = 'sending'
            mailing.save()
send_mailing.short_description = "Отправить рассылку"

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ['id', 'text_preview', 'status', 'created_at', 'sent_at', 'total_count', 'success_count', 'error_count']
    actions = [send_mailing]
    readonly_fields = ['total_count', 'success_count', 'error_count', 'sent_at']

    def text_preview(self, obj):
        return obj.text[:50]
    text_preview.short_description = 'Текст'

@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ['mailing', 'user', 'status', 'created_at']
    list_filter = ['status']