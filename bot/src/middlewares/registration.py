from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy import select
from ..database import async_session_maker
from ..models import User


class RegistrationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        aiogram_user = getattr(event, "from_user", None)
        if not aiogram_user or not async_session_maker:
            return await handler(event, data)

        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == aiogram_user.id)
            )
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    telegram_id=aiogram_user.id,
                    username=aiogram_user.username,
                    first_name=aiogram_user.first_name,
                    last_name=aiogram_user.last_name,
                )
                session.add(user)
                await session.commit()
            else:
                if (
                    user.username != aiogram_user.username
                    or user.first_name != aiogram_user.first_name
                    or user.last_name != aiogram_user.last_name
                ):
                    user.username = aiogram_user.username
                    user.first_name = aiogram_user.first_name
                    user.last_name = aiogram_user.last_name
                    await session.commit()

            data["db_user"] = user

        return await handler(event, data)
