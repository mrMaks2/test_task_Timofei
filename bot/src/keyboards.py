from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .models import Channel
from .config import settings
from .callbacks import CartActionCb, CartItemCb, CatalogRootCb


def subscription_keyboard(channels: list[Channel]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        title = ch.title or "канал"
        handle = ch.chat_id.strip("@")
        builder.button(text=f"Подписаться на {title}", url=f"https://t.me/{handle}")
    builder.button(text="Проверить подписку", callback_data="check_subscription")
    builder.adjust(1)
    return builder.as_markup()


def phone_keyboard() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text="Поделиться контактом", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Каталог", callback_data=CatalogRootCb(page=1).pack())
    builder.button(text="Корзина", callback_data="cart")
    builder.button(text="FAQ", switch_inline_query_current_chat="")
    builder.button(
        text="Открыть WebApp",
        web_app=WebAppInfo(url=settings.WEBAPP_URL),
    )
    builder.adjust(1)
    return builder.as_markup()


def product_keyboard(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="В корзину", callback_data=f"add_to_cart:{product_id}")
    builder.button(text="Назад", callback_data=CatalogRootCb(page=1).pack())
    builder.adjust(1)
    return builder.as_markup()


def cart_keyboard(cart_items: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in cart_items:
        builder.button(
            text=f"{item.product.name} - {item.quantity} шт.",
            callback_data=CartItemCb(id=item.id).pack(),
        )
        builder.button(
            text="➖",
            callback_data=CartActionCb(action="decr", item_id=item.id).pack(),
        )
        builder.button(
            text="➕",
            callback_data=CartActionCb(action="incr", item_id=item.id).pack(),
        )
        builder.button(
            text="Удалить",
            callback_data=CartActionCb(action="remove", item_id=item.id).pack(),
        )
    builder.button(text="Очистить корзину", callback_data=CartActionCb(action="clear").pack())
    builder.button(text="Оформить заказ", callback_data="checkout")
    builder.button(text="Назад", callback_data="main_menu")
    builder.adjust(1, 3)
    return builder.as_markup()
