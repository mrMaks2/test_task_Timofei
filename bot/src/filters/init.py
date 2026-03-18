from aiogram.filters import BaseFilter
from aiogram.types import Message
from ..config import settings


class IsAdminFilter(BaseFilter):
    """
    Custom filter for admin users based on ADMIN_IDS env.
    """

    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        return message.from_user.id in settings.admin_ids


class IsSubscribedFilter(BaseFilter):
    """
    Placeholder for additional subscription checks.
    """

    async def __call__(self, message: Message) -> bool:
        return True
