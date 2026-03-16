from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func
from datetime import datetime, timedelta

from ..database import async_session_maker
from ..models import User, Order, Cart, CartItem, Category, Product
from ..keyboards import main_menu_keyboard
from ..filters import IsAdminFilter

router = Router()

# Команда /start (уже есть в start.py, но добавим хелпер)
@router.message(Command('start'))
async def cmd_start(message: Message, db_user: User):
    """Обработчик команды /start (уже реализован в start.py)"""
    pass  # Этот обработчик будет переопределен в start.py

# Команда /help
@router.message(Command('help'))
async def cmd_help(message: Message):
    """Показать справку по командам бота"""
    help_text = """
<b>🤖 Доступные команды:</b>

/start - Запустить бота и главное меню
/catalog - Открыть каталог товаров
/cart - Показать корзину
/help - Показать эту справку
/profile - Информация о профиле
/faq - Часто задаваемые вопросы
/support - Связаться с поддержкой

<b>🛍 Как сделать заказ:</b>
1. Выберите товары в каталоге
2. Добавьте их в корзину
3. Перейдите в корзину и оформите заказ
4. Подтвердите данные доставки

По вопросам работы бота обращайтесь в поддержку.
    """
    
    # Создаем клавиатуру с кнопками
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 Каталог", callback_data="catalog")
    builder.button(text="🛒 Корзина", callback_data="cart")
    builder.button(text="❓ FAQ", switch_inline_query_current_chat="")
    builder.button(text="📞 Поддержка", url="https://t.me/support")
    builder.adjust(2)
    
    await message.answer(
        help_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

# Команда /catalog
@router.message(Command('catalog'))
async def cmd_catalog(message: Message):
    """Открыть каталог товаров"""
    async with async_session_maker() as session:
        # Получаем корневые категории
        categories = await session.execute(
            select(Category).where(
                Category.parent_id.is_(None),
                Category.is_active == True
            ).order_by(Category.order)
        )
        categories = categories.scalars().all()
    
    if not categories:
        await message.answer("📭 Каталог временно пуст. Попробуйте позже.")
        return
    
    builder = InlineKeyboardBuilder()
    for cat in categories:
        # Получаем количество товаров в категории
        async with async_session_maker() as session:
            product_count = await session.execute(
                select(func.count(Product.id)).where(
                    Product.category_id == cat.id,
                    Product.is_active == True
                )
            )
            count = product_count.scalar()
        
        button_text = f"{cat.name}"
        if count:
            button_text += f" ({count})"
        
        builder.button(text=button_text, callback_data=f"cat_{cat.id}")
    
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    
    await message.answer(
        "📋 <b>Категории товаров:</b>\nВыберите интересующую категорию:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

# Команда /cart
@router.message(Command('cart'))
async def cmd_cart(message: Message, db_user: User):
    """Показать корзину пользователя"""
    async with async_session_maker() as session:
        # Получаем корзину пользователя
        cart = await session.execute(
            select(Cart).where(Cart.user_id == db_user.id)
        )
        cart = cart.scalar_one_or_none()
        
        if not cart:
            await message.answer("🛒 Ваша корзина пуста.")
            return
        
        # Получаем товары в корзине
        items = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        items = items.scalars().all()
        
        if not items:
            await message.answer("🛒 Ваша корзина пуста.")
            return
        
        # Формируем сообщение с корзиной
        cart_text = "🛒 <b>Ваша корзина:</b>\n\n"
        total = 0
        
        for i, item in enumerate(items, 1):
            item_total = item.product.price * item.quantity
            total += item_total
            cart_text += (
                f"{i}. <b>{item.product.name}</b>\n"
                f"   {item.quantity} шт. × {item.product.price} руб. = {item_total} руб.\n"
            )
        
        cart_text += f"\n💰 <b>Итого: {total} руб.</b>"
        
        # Создаем клавиатуру для корзины
        builder = InlineKeyboardBuilder()
        builder.button(text="✏️ Редактировать", callback_data="cart")
        builder.button(text="✅ Оформить заказ", callback_data="checkout")
        builder.button(text="🗑 Очистить", callback_data="clear_cart")
        builder.button(text="🔙 В каталог", callback_data="catalog")
        builder.adjust(2)
        
        await message.answer(
            cart_text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

# Команда /profile (дополнительная полезная команда)
@router.message(Command('profile'))
async def cmd_profile(message: Message, db_user: User):
    """Показать информацию о профиле пользователя"""
    async with async_session_maker() as session:
        # Получаем статистику заказов
        orders = await session.execute(
            select(Order).where(Order.user_id == db_user.id).order_by(Order.created_at.desc())
        )
        orders = orders.scalars().all()
        
        total_orders = len(orders)
        completed_orders = sum(1 for o in orders if o.status == 'delivered')
        total_spent = sum(o.total for o in orders if o.status in ['delivered', 'paid'])
    
    profile_text = f"""
<b>👤 Ваш профиль:</b>

🆔 Telegram ID: <code>{db_user.telegram_id}</code>
📱 Телефон: {db_user.phone or 'не указан'}
👤 Имя: {db_user.first_name or 'не указано'}
📝 Username: @{db_user.username if db_user.username else 'не указан'}

<b>📊 Статистика:</b>
📦 Всего заказов: {total_orders}
✅ Выполнено: {completed_orders}
💰 Потрачено всего: {total_spent} руб.
📅 Зарегистрирован: {db_user.created_at.strftime('%d.%m.%Y')}
    """
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Мои заказы", callback_data="my_orders")
    builder.button(text="✏️ Редактировать профиль", callback_data="edit_profile")
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    
    await message.answer(
        profile_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

# Команда /faq
@router.message(Command('faq'))
async def cmd_faq(message: Message):
    """Показать часто задаваемые вопросы"""
    async with async_session_maker() as session:
        from ..models import FAQ
        faqs = await session.execute(
            select(FAQ).where(FAQ.is_active == True).order_by(FAQ.order).limit(5)
        )
        faqs = faqs.scalars().all()
    
    if not faqs:
        await message.answer("❓ FAQ временно недоступен.")
        return
    
    faq_text = "❓ <b>Часто задаваемые вопросы:</b>\n\n"
    for i, faq in enumerate(faqs, 1):
        faq_text += f"<b>{i}. {faq.question}</b>\n{faq.answer}\n\n"
    
    faq_text += "\n💡 Чтобы найти ответ на конкретный вопрос, введите @botname ваш вопрос в любом чате."
    
    await message.answer(faq_text, parse_mode="HTML")

# Команда /support
@router.message(Command('support'))
async def cmd_support(message: Message):
    """Связаться с поддержкой"""
    support_text = """
<b>📞 Служба поддержки</b>

Если у вас возникли вопросы или проблемы:
• Напишите в чат поддержки: @support_chat
• Или отправьте сообщение на email: support@example.com

⏰ Время работы: круглосуточно
🕐 Среднее время ответа: до 1 часа
    """
    
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Чат поддержки", url="https://t.me/support_chat")
    builder.button(text="✉️ Написать письмо", url="mailto:support@example.com")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(1)
    
    await message.answer(
        support_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

# Команда для администраторов (с фильтром)
@router.message(Command('admin'), IsAdminFilter())
async def cmd_admin_panel(message: Message):
    """Панель администратора (только для админов)"""
    admin_text = """
<b>🔐 Панель администратора</b>

<b>📊 Статистика:</b>
"""
    
    async with async_session_maker() as session:
        # Общая статистика
        total_users = await session.execute(select(func.count(User.id)))
        total_users = total_users.scalar()
        
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        new_users_today = await session.execute(
            select(func.count(User.id)).where(
                func.date(User.created_at) == today
            )
        )
        new_users_today = new_users_today.scalar()
        
        total_orders = await session.execute(select(func.count(Order.id)))
        total_orders = total_orders.scalar()
        
        new_orders_today = await session.execute(
            select(func.count(Order.id)).where(
                func.date(Order.created_at) == today
            )
        )
        new_orders_today = new_orders_today.scalar()
        
        admin_text += f"""
👥 Всего пользователей: {total_users}
📈 Новых сегодня: {new_users_today}
📦 Всего заказов: {total_orders}
🆕 Новых заказов сегодня: {new_orders_today}

<b>⚙️ Управление:</b>
        """
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Заказы", callback_data="admin_orders")
    builder.button(text="👥 Пользователи", callback_data="admin_users")
    builder.button(text="📊 Полная статистика", callback_data="admin_stats")
    builder.button(text="📨 Рассылки", callback_data="admin_mailings")
    builder.button(text="⚙️ Настройки", callback_data="admin_settings")
    builder.adjust(2)
    
    await message.answer(
        admin_text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

# Команда для просмотра своих заказов
@router.message(Command('myorders'))
async def cmd_my_orders(message: Message, db_user: User):
    """Показать историю заказов пользователя"""
    async with async_session_maker() as session:
        orders = await session.execute(
            select(Order).where(Order.user_id == db_user.id).order_by(Order.created_at.desc()).limit(10)
        )
        orders = orders.scalars().all()
    
    if not orders:
        await message.answer("У вас пока нет заказов. 🛍")
        return
    
    status_emojis = {
        'new': '🆕',
        'paid': '✅',
        'shipped': '📦',
        'delivered': '🎉',
        'cancelled': '❌'
    }
    
    orders_text = "📋 <b>Ваши последние заказы:</b>\n\n"
    for order in orders:
        emoji = status_emojis.get(order.status, '📄')
        orders_text += (
            f"{emoji} <b>Заказ #{order.id}</b>\n"
            f"   Статус: {order.get_status_display()}\n"
            f"   Сумма: {order.total} руб.\n"
            f"   Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        )
    
    await message.answer(orders_text, parse_mode="HTML")