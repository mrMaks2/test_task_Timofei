from aiohttp import web
from aiogram import Bot
from ..config import settings
from ..database import async_session_maker
from ..models import User, Order

async def process_notification(request: web.Request):
    # Проверка токена
    auth = request.headers.get('Authorization')
    if auth != f'Bearer {settings.BOT_INTERNAL_TOKEN}':
        return web.Response(status=403)

    data = await request.json()
    event = data.get('event')
    if event == 'order_status_changed':
        order_id = data['order_id']
        new_status = data['new_status']
        async with async_session_maker() as session:
            order = await session.get(Order, order_id)
            if order:
                user = await session.get(User, order.user_id)
                if user:
                    bot = Bot(token=settings.BOT_TOKEN)
                    await bot.send_message(
                        user.telegram_id,
                        f"Статус вашего заказа #{order.id} изменён на: {new_status}"
                    )
    return web.Response(status=200)