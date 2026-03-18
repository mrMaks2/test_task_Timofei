from django.contrib import admin
from django.http import HttpResponse
from django.conf import settings
import openpyxl
import requests
import logging
from .models import Order, OrderItem

logger = logging.getLogger(__name__)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

def export_paid_orders(modeladmin, request, queryset):
    queryset = queryset.filter(status='paid')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Оплаченные заказы"
    ws.append(['ID', 'Клиент', 'Телефон', 'Сумма', 'Дата'])
    for order in queryset:
        ws.append([order.id, order.full_name, order.phone, str(order.total), order.created_at])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=paid_orders.xlsx'
    wb.save(response)
    return response
export_paid_orders.short_description = "Экспортировать оплаченные заказы в Excel"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__telegram_id', 'full_name', 'phone']
    inlines = [OrderItemInline]
    actions = [export_paid_orders]
    readonly_fields = ['total', 'created_at']

    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_status = Order.objects.filter(pk=obj.pk).values_list("status", flat=True).first()
        super().save_model(request, obj, form, change)
        if change and old_status and old_status != obj.status and settings.BOT_INTERNAL_TOKEN:
            try:
                requests.post(
                    settings.BOT_WEBHOOK_URL,
                    json={
                        "event": "order_status_changed",
                        "order_id": obj.id,
                        "new_status": obj.status,
                    },
                    headers={"Authorization": f"Bearer {settings.BOT_INTERNAL_TOKEN}"},
                    timeout=5,
                )
            except Exception as exc:
                logger.error("Failed to notify bot about status change: %s", exc)
