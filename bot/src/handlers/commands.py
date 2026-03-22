from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime

import src.database as db
from src.models import User, Order, Cart, CartItem, Category, Product, FAQ
from src.keyboards import main_menu_keyboard
from src.filters import IsAdminFilter

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "<b>Доступные команды:</b>\n\n"
        "/start - Запустить бота и главное меню\n"
        "/catalog - Открыть каталог товаров\n"
        "/cart - Показать корзину\n"
        "/help - Показать эту справку\n"
        "/profile - Информация о профиле\n"
        "/faq - Часто задаваемые вопросы\n"
        "/support - Связаться с поддержкой\n"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="Каталог", callback_data="catalog:1")
    builder.button(text="Корзина", callback_data="cart")
    builder.button(text="FAQ", switch_inline_query_current_chat="")
    builder.button(text="Поддержка", url="https://t.me/support")
    builder.adjust(2)

    await message.answer(help_text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.message(Command("catalog"))
async def cmd_catalog(message: Message):
    async with db.async_session_maker() as session:
        result = await session.execute(
            select(Category)
            .where(Category.parent_id.is_(None), Category.is_active == True)
            .order_by(Category.order)
        )
        categories = result.scalars().all()

        if not categories:
            await message.answer("Каталог временно пуст. Попробуйте позже.")
            return

        builder = InlineKeyboardBuilder()
        for cat in categories:
            product_count = await session.execute(
                select(func.count(Product.id)).where(
                    Product.category_id == cat.id, Product.is_active == True
                )
            )
            count = product_count.scalar()
            button_text = f"{cat.name} ({count})" if count else cat.name
            builder.button(text=button_text, callback_data=f"cat:{cat.id}:1")

    builder.button(text="Главное меню", callback_data="main_menu")
    builder.adjust(1)

    await message.answer(
        "<b>Категории товаров:</b>\nВыберите интересующую категорию:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.message(Command("cart"))
async def cmd_cart(message: Message, db_user: User):
    async with db.async_session_maker() as session:
        cart_result = await session.execute(
            select(Cart).where(Cart.user_id == db_user.id)
        )
        cart = cart_result.scalar_one_or_none()

        if not cart:
            await message.answer("Ваша корзина пуста.")
            return

        items_result = await session.execute(
            select(CartItem)
            .where(CartItem.cart_id == cart.id)
            .options(selectinload(CartItem.product))
        )
        items = items_result.scalars().all()

        if not items:
            await message.answer("Ваша корзина пуста.")
            return

        cart_text = "<b>Ваша корзина:</b>\n\n"
        total = 0

        for i, item in enumerate(items, 1):
            item_total = item.product.price * item.quantity
            total += item_total
            cart_text += (
                f"{i}. <b>{item.product.name}</b>\n"
                f"   {item.quantity} шт. × {item.product.price} руб. = {item_total} руб.\n"
            )

        cart_text += f"\n<b>Итого: {total} руб.</b>"

    builder = InlineKeyboardBuilder()
    builder.button(text="Редактировать", callback_data="cart")
    builder.button(text="Оформить заказ", callback_data="checkout")
    builder.button(text="Очистить", callback_data="cart_action:clear:0")
    builder.button(text="В каталог", callback_data="catalog:1")
    builder.adjust(2)

    await message.answer(cart_text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.message(Command("profile"))
async def cmd_profile(message: Message, db_user: User):
    async with db.async_session_maker() as session:
        orders_result = await session.execute(
            select(Order).where(Order.user_id == db_user.id).order_by(Order.created_at.desc())
        )
        orders = orders_result.scalars().all()

    total_orders = len(orders)
    completed_orders = sum(1 for o in orders if o.status == "delivered")
    total_spent = sum(o.total for o in orders if o.status in ["delivered", "paid"])

    profile_text = (
        "<b>Ваш профиль:</b>\n\n"
        f"Telegram ID: <code>{db_user.telegram_id}</code>\n"
        f"Телефон: {db_user.phone or 'не указан'}\n"
        f"Имя: {db_user.first_name or 'не указано'}\n"
        f"Username: @{db_user.username if db_user.username else 'не указан'}\n\n"
        "<b>Статистика:</b>\n"
        f"Всего заказов: {total_orders}\n"
        f"Выполнено: {completed_orders}\n"
        f"Потрачено всего: {total_spent} руб.\n"
        f"Дата регистрации: {db_user.created_at.strftime('%d.%m.%Y')}\n"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="Мои заказы", callback_data="my_orders")
    builder.button(text="Главное меню", callback_data="main_menu")
    builder.adjust(1)

    await message.answer(profile_text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.message(Command("faq"))
async def cmd_faq(message: Message):
    async with db.async_session_maker() as session:
        faqs_result = await session.execute(
            select(FAQ).where(FAQ.is_active == True).order_by(FAQ.order).limit(5)
        )
        faqs = faqs_result.scalars().all()

    if not faqs:
        await message.answer("FAQ временно недоступен.")
        return

    faq_text = "<b>Часто задаваемые вопросы:</b>\n\n"
    for i, faq in enumerate(faqs, 1):
        faq_text += f"<b>{i}. {faq.question}</b>\n{faq.answer}\n\n"

    faq_text += (
        "\nЧтобы найти ответ на конкретный вопрос, введите @botname "
        "ваш вопрос в любом чате."
    )

    await message.answer(faq_text, parse_mode="HTML")


@router.message(Command("support"))
async def cmd_support(message: Message):
    support_text = (
        "<b>Служба поддержки</b>\n\n"
        "Если у вас возникли вопросы или проблемы:\n"
        "• Напишите в чат поддержки: @support_chat\n"
        "• Или отправьте сообщение на email: support@example.com\n\n"
        "Время работы: круглосуточно\n"
        "Среднее время ответа: до 1 часа"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="Чат поддержки", url="https://t.me/support_chat")
    builder.button(text="Написать письмо", url="mailto:support@example.com")
    builder.button(text="Назад", callback_data="main_menu")
    builder.adjust(1)

    await message.answer(support_text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.message(Command("admin"), IsAdminFilter())
async def cmd_admin_panel(message: Message):
    admin_text = "<b>Панель администратора</b>\n\n<b>Статистика:</b>\n"

    async with db.async_session_maker() as session:
        total_users = (await session.execute(select(func.count(User.id)))).scalar()

        today = datetime.now().date()
        new_users_today = (
            await session.execute(select(func.count(User.id)).where(func.date(User.created_at) == today))
        ).scalar()

        total_orders = (await session.execute(select(func.count(Order.id)))).scalar()
        new_orders_today = (
            await session.execute(select(func.count(Order.id)).where(func.date(Order.created_at) == today))
        ).scalar()

    admin_text += (
        f"Всего пользователей: {total_users}\n"
        f"Новых сегодня: {new_users_today}\n"
        f"Всего заказов: {total_orders}\n"
        f"Новых заказов сегодня: {new_orders_today}\n\n"
        "<b>Управление:</b>"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="Заказы", callback_data="admin_orders")
    builder.button(text="Пользователи", callback_data="admin_users")
    builder.button(text="Статистика", callback_data="admin_stats")
    builder.button(text="Рассылки", callback_data="admin_mailings")
    builder.button(text="Настройки", callback_data="admin_settings")
    builder.adjust(2)

    await message.answer(admin_text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.message(Command("myorders"))
async def cmd_my_orders(message: Message, db_user: User):
    async with db.async_session_maker() as session:
        orders_result = await session.execute(
            select(Order)
            .where(Order.user_id == db_user.id)
            .order_by(Order.created_at.desc())
            .limit(10)
        )
        orders = orders_result.scalars().all()

    if not orders:
        await message.answer("У вас пока нет заказов.")
        return

    status_names = {
        "new": "Новый",
        "paid": "Оплачен",
        "shipped": "Отправлен",
        "delivered": "Доставлен",
        "cancelled": "Отменен",
    }

    orders_text = "<b>Ваши последние заказы:</b>\n\n"
    for order in orders:
        status = status_names.get(order.status, order.status)
        orders_text += (
            f"<b>Заказ #{order.id}</b>\n"
            f"Статус: {status}\n"
            f"Сумма: {order.total} руб.\n"
            f"Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        )

    await message.answer(orders_text, parse_mode="HTML")


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu_keyboard())

@router.callback_query(F.data == "webapp_unavailable")
async def callback_webapp_unavailable(callback: types.CallbackQuery):
    await callback.answer("WebApp требует публичный HTTPS URL (localhost не подходит).", show_alert=True)

@router.message(lambda msg: msg.text is not None and not msg.text.startswith("/"))
async def fallback_message(message: Message):
    await message.answer(
        "Я не понял ваш запрос. Используйте команды /help, /catalog, /cart.",
        reply_markup=main_menu_keyboard(),
    )
