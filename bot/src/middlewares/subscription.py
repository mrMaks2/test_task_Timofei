from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from sqlalchemy import select
from ..database import async_session_maker
from ..models import Channel
from ..keyboards import subscription_keyboard

class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Пропускаем проверку для callback от кнопки проверки подписки и команды /start
        if isinstance(event, CallbackQuery) and event.data == 'check_subscription':
            return await handler(event, data)
        if isinstance(event, Message) and event.text == '/start':
            return await handler(event, data)

        user = data.get('db_user')
        if not user:
            return await handler(event, data)

        bot: Bot = data['bot']
        async with async_session_maker() as session:
            channels = await session.execute(
                select(Channel).where(Channel.is_mandatory == True)
            )
            channels = channels.scalars().all()

        not_subscribed = []
        for channel in channels:
            try:
                member = await bot.get_chat_member(chat_id=channel.chat_id, user_id=user.telegram_id)
                if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
                    not_subscribed.append(channel)
            except Exception:
                not_subscribed.append(channel)

        if not_subscribed:
            if isinstance(event, Message):
                await event.answer(
                    "Для доступа к боту подпишитесь на каналы:",
                    reply_markup=subscription_keyboard(not_subscribed)
                )
            elif isinstance(event, CallbackQuery):
                await event.message.answer(
                    "Для доступа к боту подпишитесь на каналы:",
                    reply_markup=subscription_keyboard(not_subscribed)
                )
            return  # прерываем обработку
        return await handler(event, data)