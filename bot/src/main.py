import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from src.config import settings
from src.database import init_db, close_db
from src.middlewares.registration import RegistrationMiddleware
from src.middlewares.subscription import SubscriptionMiddleware
from src.middlewares.logging_mw import LoggingMiddleware
from src.handlers import (
    start, catalog, cart, order, inline,
    admin_chat, commands, notifications
)
from src.utils.set_commands import set_bot_commands

logger = logging.getLogger(__name__)

async def on_startup(bot: Bot, dispatcher: Dispatcher):
    await init_db()
    await set_bot_commands(bot)
    logger.info("Bot started")

async def on_shutdown(bot: Bot, dispatcher: Dispatcher):
    await close_db()
    logger.info("Bot stopped")

async def handle_notification(request: web.Request):
    from src.handlers.notifications import process_notification
    return await process_notification(request)

async def start_webhook_server():
    app = web.Application()
    app.router.add_post('/notify', handle_notification)
    app.router.add_get('/health', lambda request: web.Response(text="ok"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8081)
    await site.start()
    logger.info("Notification server started on port 8081")
    return runner

async def main():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    handlers = [
        logging.StreamHandler(),
        RotatingFileHandler(
            log_dir / "bot.log", maxBytes=5 * 1024 * 1024, backupCount=5
        ),
    ]
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )
    await init_db()
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
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
