from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from sqlalchemy import delete, select
from ..database import async_session_maker
from ..models import Order, OrderItem, Cart, CartItem, User

router = Router()

class OrderFSM(StatesGroup):
    full_name = State()
    address = State()
    confirm = State()

@router.callback_query(F.data == 'checkout')
async def start_order(callback: CallbackQuery, state: FSMContext, db_user: User):
    if not db_user.phone:
        await callback.answer("Сначала укажите телефон через /start", show_alert=True)
        return
    await callback.message.edit_text("Введите ваше ФИО:")
    await state.set_state(OrderFSM.full_name)

@router.message(OrderFSM.full_name)
async def process_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Введите адрес доставки:")
    await state.set_state(OrderFSM.address)

@router.message(OrderFSM.address)
async def process_address(message: Message, state: FSMContext, db_user: User):
    data = await state.get_data()
    data['address'] = message.text
    data['phone'] = db_user.phone

    # Подсчёт итога из корзины
    async with async_session_maker() as session:
        cart = await session.execute(select(Cart).where(Cart.user_id == db_user.id))
        cart = cart.scalar_one_or_none()
        if not cart:
            await message.answer("Корзина пуста.")
            await state.clear()
            return
        items = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        items = items.scalars().all()
        total = sum(item.product.price * item.quantity for item in items)

    # Показ подтверждения
    await message.answer(
        f"Подтвердите заказ:\n\n"
        f"ФИО: {data['full_name']}\n"
        f"Адрес: {data['address']}\n"
        f"Телефон: {data['phone']}\n"
        f"Сумма: {total} руб.\n\n"
        "Всё верно?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да", callback_data="confirm_order")],
            [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_order")]
        ])
    )
    await state.set_state(OrderFSM.confirm)

@router.callback_query(OrderFSM.confirm, F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext, db_user: User):
    data = await state.get_data()
    async with async_session_maker() as session:
        # Создаём заказ
        cart = await session.execute(select(Cart).where(Cart.user_id == db_user.id))
        cart = cart.scalar_one()
        items = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        items = items.scalars().all()
        total = sum(item.product.price * item.quantity for item in items)

        order = Order(
            user_id=db_user.id,
            full_name=data['full_name'],
            address=data['address'],
            phone=data['phone'],
            total=total,
            status='new'
        )
        session.add(order)
        await session.flush()

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price
            )
            session.add(order_item)

        # Очищаем корзину
        await session.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
        await session.commit()

    # Уведомление админам (отправка в чат)
    await callback.bot.send_message(
        chat_id=...,
        text=f"Новый заказ #{order.id} на сумму {total} руб."
    )

    await callback.message.edit_text("Заказ оформлен! Ожидайте подтверждения.")
    await state.clear()