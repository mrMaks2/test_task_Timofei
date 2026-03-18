from aiogram.filters import BaseFilter
from aiogram.types import Message
from ..config import settings


class IsAdminFilter(BaseFilter):
    """
    Кастомный фильтр для админов на основе переменной ADMIN_IDS.
    """

    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        return message.from_user.id in settings.admin_ids


class IsSubscribedFilter(BaseFilter):
    """
    Заглушка для дополнительных проверок подписки.
    """

    async def __call__(self, message: Message) -> bool:
        return True
