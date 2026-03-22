from aiogram import Router, types, F
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
import src.database as db
from src.models import Cart, CartItem, User
from src.keyboards import cart_keyboard
from src.callbacks import CartActionCb

router = Router()


async def get_or_create_cart(user: User) -> Cart:
    async with db.async_session_maker() as session:
        result = await session.execute(select(Cart).where(Cart.user_id == user.id))
        cart = result.scalar_one_or_none()
        if not cart:
            cart = Cart(user_id=user.id)
            session.add(cart)
            await session.commit()
        return cart


async def fetch_cart_items(cart_id: int):
    async with db.async_session_maker() as session:
        result = await session.execute(
            select(CartItem)
            .where(CartItem.cart_id == cart_id)
            .options(selectinload(CartItem.product))
        )
        items = result.scalars().all()
    total = sum(item.product.price * item.quantity for item in items)
    return items, total


@router.callback_query(F.data == "cart")
async def show_cart(callback: types.CallbackQuery, db_user: User):
    cart = await get_or_create_cart(db_user)
    items, total = await fetch_cart_items(cart.id)
    if not items:
        await callback.message.edit_text("Корзина пуста.")
        return
    await callback.message.edit_text(
        "Ваша корзина:\n\n"
        + "\n".join(
            f"{item.product.name} — {item.quantity} шт. = {item.product.price * item.quantity} руб."
            for item in items
        )
        + f"\n\nИтого: {total} руб.",
        reply_markup=cart_keyboard(items),
    )


@router.callback_query(F.data.startswith("add_to_cart:"))
async def add_to_cart(callback: types.CallbackQuery, db_user: User):
    product_id = int(callback.data.split(":")[1])
    cart = await get_or_create_cart(db_user)
    async with db.async_session_maker() as session:
        item_result = await session.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id, CartItem.product_id == product_id
            )
        )
        item = item_result.scalar_one_or_none()
        if item:
            item.quantity += 1
        else:
            item = CartItem(cart_id=cart.id, product_id=product_id, quantity=1)
            session.add(item)
        await session.commit()
    await callback.answer("Товар добавлен в корзину", show_alert=False)
    await show_cart(callback, db_user)


@router.callback_query(F.data.startswith("cart_action:"))
async def cart_action(callback: types.CallbackQuery, db_user: User):
    data = CartActionCb.unpack(callback.data)
    action = data.action
    item_id = data.item_id

    cart = await get_or_create_cart(db_user)
    async with db.async_session_maker() as session:
        if action == "clear":
            await session.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
            await session.commit()
            await callback.message.edit_text("Корзина очищена.")
            return

        if item_id:
            item = await session.get(CartItem, item_id)
            if not item or item.cart_id != cart.id:
                await callback.answer("Элемент не найден.")
                return
            if action == "incr":
                item.quantity += 1
            elif action == "decr":
                item.quantity -= 1
                if item.quantity <= 0:
                    await session.delete(item)
            elif action == "remove":
                await session.delete(item)
            await session.commit()

    await show_cart(callback, db_user)


@router.callback_query(F.data.startswith("cart_item:"))
async def cart_item_hint(callback: types.CallbackQuery):
    await callback.answer("Выберите действие для товара кнопками ниже.")
