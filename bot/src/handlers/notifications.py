from aiohttp import web
from aiogram import Bot, Router
import asyncio
from src.config import settings
import src.database as db
from sqlalchemy import select
from src.models import User, Order, Mailing, MailingLog

router = Router()


async def _run_mailing(mailing_id: int) -> None:
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        async with db.async_session_maker() as session:
            mailing = await session.get(Mailing, mailing_id)
            if not mailing:
                return
            users = (await session.execute(select(User))).scalars().all()
            text = mailing.text
            image = mailing.image
            mailing.total_count = len(users)
            mailing.success_count = 0
            mailing.error_count = 0
            mailing.status = "sending"
            await session.commit()

        success_count = 0
        error_count = 0
        for user in users:
            try:
                if image:
                    await bot.send_photo(user.telegram_id, image, caption=text)
                else:
                    await bot.send_message(user.telegram_id, text)
                status = "success"
                error_message = None
                success_count += 1
            except Exception as exc:
                status = "error"
                error_message = str(exc)
                error_count += 1

            async with db.async_session_maker() as session:
                log = MailingLog(
                    mailing_id=mailing_id,
                    user_id=user.id,
                    status=status,
                    error_message=error_message,
                )
                session.add(log)
                await session.commit()

        async with db.async_session_maker() as session:
            mailing = await session.get(Mailing, mailing_id)
            if mailing:
                mailing.status = "sent"
                mailing.success_count = success_count
                mailing.error_count = error_count
                await session.commit()
    finally:
        await bot.session.close()


async def process_notification(request: web.Request):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {settings.BOT_INTERNAL_TOKEN}":
        return web.Response(status=403)

    data = await request.json()
    event = data.get("event")

    bot = Bot(token=settings.BOT_TOKEN)
    try:
        if event == "order_status_changed":
            order_id = data["order_id"]
            new_status = data["new_status"]
            async with db.async_session_maker() as session:
                order = await session.get(Order, order_id)
                if order:
                    user = await session.get(User, order.user_id)
                    if user:
                        await bot.send_message(
                            user.telegram_id,
                            f"Статус вашего заказа #{order.id} изменен на: {new_status}",
                        )
        elif event == "new_order":
            chat_id = data.get("chat_id")
            message = data.get("message")
            if chat_id and message:
                await bot.send_message(chat_id, message, parse_mode="HTML")
        elif event == "start_mailing":
            mailing_id = data.get("mailing_id")
            if mailing_id:
                asyncio.create_task(_run_mailing(int(mailing_id)))
    finally:
        await bot.session.close()

    return web.Response(status=200)
