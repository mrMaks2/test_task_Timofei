from django.contrib import admin
from django.conf import settings
import requests
import logging
from .models import Mailing, MailingLog

logger = logging.getLogger(__name__)


def send_mailing(modeladmin, request, queryset):
    for mailing in queryset.filter(status="ready"):
        if not settings.BOT_INTERNAL_TOKEN:
            continue
        try:
            response = requests.post(
                settings.BOT_WEBHOOK_URL,
                json={"event": "start_mailing", "mailing_id": mailing.id},
                headers={"Authorization": f"Bearer {settings.BOT_INTERNAL_TOKEN}"},
                timeout=5,
            )
            if response.status_code == 200:
                mailing.status = "sending"
                mailing.save(update_fields=["status"])
        except Exception as exc:
            logger.error("Failed to start mailing: %s", exc)


send_mailing.short_description = "Отправить рассылку"


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "text_preview",
        "status",
        "created_at",
        "sent_at",
        "total_count",
        "success_count",
        "error_count",
    ]
    actions = [send_mailing]
    readonly_fields = ["total_count", "success_count", "error_count", "sent_at"]

    def text_preview(self, obj):
        return obj.text[:50]

    text_preview.short_description = "Текст"


@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ["mailing", "user", "status", "created_at"]
    list_filter = ["status"]
