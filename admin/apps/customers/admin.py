from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'username', 'first_name', 'last_name', 'phone', 'created_at']
    search_fields = ['telegram_id', 'username', 'phone']
    list_filter = ['created_at']