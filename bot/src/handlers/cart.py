from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup
from sqlalchemy import select, delete
from ..database import async_session_maker
from ..models import Cart, CartItem, User, Product
from ..keyboards import cart_keyboard

router = Router()

async def get_or_create_cart(user: User):
    async with async_session_maker() as session:
        cart = await session.execute(select(Cart).where(Cart.user_id == user.id))
        cart = cart.scalar_one_or_none()
        if not cart:
            cart = Cart(user_id=user.id)
            session.add(cart)
            await session.commit()
        return cart

@router.callback_query(F.data == 'cart')
async def show_cart(callback: types.CallbackQuery, db_user: User):
    cart = await get_or_create_cart(db_user)
    async with async_session_maker() as session:
        items = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        items = items.scalars().all()
        total = sum(item.product.price * item.quantity for item in items)
    if not items:
        await callback.message.edit_text("Корзина пуста.")
        return
    await callback.message.edit_text(
        f"Ваша корзина:\n\n" + "\n".join(
            f"{item.product.name} — {item.quantity} шт. = {item.product.price * item.quantity} руб."
            for item in items
        ) + f"\n\nИтого: {total} руб.",
        reply_markup=cart_keyboard(items, total)
    )

@router.callback_query(F.data.startswith('add_to_cart:'))
async def add_to_cart(callback: types.CallbackQuery, db_user: User):
    product_id = int(callback.data.split(':')[1])
    cart = await get_or_create_cart(db_user)
    async with async_session_maker() as session:
        # Проверяем, есть ли уже такой товар
        item = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        )
        item = item.scalar_one_or_none()
        if item:
            item.quantity += 1
        else:
            item = CartItem(cart_id=cart.id, product_id=product_id, quantity=1)
            session.add(item)
        await session.commit()
    await callback.answer("Товар добавлен в корзину", show_alert=False)
    await show_cart(callback, db_user)