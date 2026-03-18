from django.utils.deprecation import MiddlewareMixin
from .auth import validate_telegram_init_data, get_user_from_init_data
from apps.customers.models import Customer


class TelegramAuthMiddleware(MiddlewareMixin):
    """
    Middleware для проверки initData от Telegram WebApp.
    """

    def process_request(self, request):
        init_data = request.headers.get("X-Telegram-Init-Data")
        if init_data and validate_telegram_init_data(init_data):
            user_data = get_user_from_init_data(init_data)
            if user_data:
                request.telegram_user = user_data
                telegram_id = user_data.get("id")
                if telegram_id:
                    customer, _ = Customer.objects.get_or_create(
                        telegram_id=telegram_id,
                        defaults={
                            "username": user_data.get("username", ""),
                            "first_name": user_data.get("first_name", ""),
                            "last_name": user_data.get("last_name", ""),
                        },
                    )
                    request.customer = customer
                    request.META["HTTP_X_TELEGRAM_ID"] = str(telegram_id)
