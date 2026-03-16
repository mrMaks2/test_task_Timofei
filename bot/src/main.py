import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from .config import settings
from .database import init_db, close_db
from .middlewares.registration import RegistrationMiddleware
from .middlewares.subscription import SubscriptionMiddleware
from .handlers import (
    start, catalog, cart, order, inline,
    admin_chat, commands, notifications
)
from .utils.set_commands import set_bot_commands

logger = logging.getLogger(__name__)

async def on_startup(bot: Bot, dispatcher: Dispatcher):
    await init_db()
    await set_bot_commands(bot)
    logger.info("Bot started")

async def on_shutdown(bot: Bot, dispatcher: Dispatcher):
    await close_db()
    logger.info("Bot stopped")

async def handle_notification(request: web.Request):
    from .handlers.notifications import process_notification
    return await process_notification(request)

async def start_webhook_server():
    app = web.Application()
    app.router.add_post('/notify', handle_notification)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()
    logger.info("Notification server started on port 8081")
    return runner

async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Middleware
    dp.message.middleware(RegistrationMiddleware())
    dp.callback_query.middleware(RegistrationMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # Routers
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)
    dp.include_router(order.router)
    dp.include_router(inline.router)
    dp.include_router(admin_chat.router)
    dp.include_router(commands.router)
    dp.include_router(notifications.router)

    runner = await start_webhook_server()
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())