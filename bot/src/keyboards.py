from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .models import Category, Channel

def subscription_keyboard(channels: list[Channel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.button(text=f"Подписаться на {ch.title or 'канал'}", url=f"https://t.me/{ch.chat_id.strip('@')}")
    builder.button(text="✅ Проверить подписку", callback_data="check_subscription")
    builder.adjust(1)
    return builder.as_markup()

def phone_keyboard() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 Каталог", callback_data="catalog")
    builder.button(text="🛒 Корзина", callback_data="cart")
    builder.button(text="❓ FAQ", switch_inline_query_current_chat="")
    builder.button(text="🌐 Открыть WebApp", web_app=...)
    builder.adjust(1)
    return builder.as_markup()

def product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ В корзину", callback_data=f"add_to_cart:{product_id}")
    builder.button(text="🔙 Назад", callback_data="catalog")
    builder.adjust(1)
    return builder.as_markup()

def cart_keyboard(cart_items: list, total: float) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in cart_items:
        builder.button(
            text=f"{item.product.name} - {item.quantity} шт. ({item.product.price*item.quantity} руб.)",
            callback_data=f"cart_item:{item.id}"
        )
    builder.button(text="➖ Уменьшить", callback_data="decr")
    builder.button(text="➕ Увеличить", callback_data="incr")
    builder.button(text="❌ Удалить", callback_data="remove")
    builder.button(text="🗑 Очистить корзину", callback_data="clear_cart")
    builder.button(text="✅ Оформить заказ", callback_data="checkout")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()