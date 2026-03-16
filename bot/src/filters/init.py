from aiogram.filters import BaseFilter
from aiogram.types import Message
from ..models import User
from ..database import async_session_maker
from sqlalchemy import select

class IsAdminFilter(BaseFilter):
    """
    Кастомный фильтр для проверки, является ли пользователь администратором
    """
    async def __call__(self, message: Message) -> bool:
        # Список ID администраторов (можно вынести в БД)
        admin_ids = [123456789, 987654321]  # Замените на реальные ID
        
        # Проверяем, есть ли пользователь в списке админов
        if message.from_user.id in admin_ids:
            return True
        
        # Или можно проверить через БД
        async with async_session_maker() as session:
            user = await session.execute(
                select(User).where(User.telegram_id == message.from_user.id)
            )
            user = user.scalar_one_or_none()
            if user and user.is_admin:  # нужно добавить поле is_admin в модель User
                return True
        
        return False

class IsSubscribedFilter(BaseFilter):
    """
    Фильтр для проверки подписки на канал
    """
    async def __call__(self, message: Message) -> bool:
        # Проверка подписки (обычно делается в middleware)
        # Здесь можно реализовать дополнительную логику
        return True