from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from ..database import async_session_maker
from ..models import Order, OrderItem, Cart, CartItem, User
from ..config import settings

router = Router()


class OrderFSM(StatesGroup):
    full_name = State()
    address = State()
    confirm = State()


@router.callback_query(F.data == "checkout")
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
    data["address"] = message.text
    data["phone"] = db_user.phone

    async with async_session_maker() as session:
        cart_result = await session.execute(select(Cart).where(Cart.user_id == db_user.id))
        cart = cart_result.scalar_one_or_none()
        if not cart:
            await message.answer("Корзина пуста.")
            await state.clear()
            return
        items_result = await session.execute(
            select(CartItem)
            .where(CartItem.cart_id == cart.id)
            .options(selectinload(CartItem.product))
        )
        items = items_result.scalars().all()
        total = sum(item.product.price * item.quantity for item in items)

    await message.answer(
        "Подтвердите заказ:\n\n"
        f"ФИО: {data['full_name']}\n"
        f"Адрес: {data['address']}\n"
        f"Телефон: {data['phone']}\n"
        f"Сумма: {total} руб.\n\n"
        "Все верно?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Да", callback_data="confirm_order")],
                [InlineKeyboardButton(text="Нет, отмена", callback_data="cancel_order")],
            ]
        ),
    )
    await state.set_state(OrderFSM.confirm)


@router.callback_query(OrderFSM.confirm, F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Заказ отменен.")
    await state.clear()


@router.callback_query(OrderFSM.confirm, F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext, db_user: User):
    data = await state.get_data()
    async with async_session_maker() as session:
        cart_result = await session.execute(select(Cart).where(Cart.user_id == db_user.id))
        cart = cart_result.scalar_one()
        items_result = await session.execute(
            select(CartItem)
            .where(CartItem.cart_id == cart.id)
            .options(selectinload(CartItem.product))
        )
        items = items_result.scalars().all()
        total = sum(item.product.price * item.quantity for item in items)

        order = Order(
            user_id=db_user.id,
            full_name=data["full_name"],
            address=data["address"],
            phone=data["phone"],
            total=total,
            status="new",
        )
        session.add(order)
        await session.flush()

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
            )
            session.add(order_item)

        await session.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
        await session.commit()

    admin_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оплачен",
                    callback_data=f"order_status:{order.id}:paid",
                ),
                InlineKeyboardButton(
                    text="Отправлен",
                    callback_data=f"order_status:{order.id}:shipped",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Доставлен",
                    callback_data=f"order_status:{order.id}:delivered",
                ),
                InlineKeyboardButton(
                    text="Отменен",
                    callback_data=f"order_status:{order.id}:cancelled",
                ),
            ],
        ]
    )

    await callback.bot.send_message(
        chat_id=settings.ADMIN_CHAT_ID,
        text=f"Новый заказ #{order.id} на сумму {total} руб.",
        reply_markup=admin_kb,
    )

    await callback.message.edit_text(
        "Заказ оформлен! Мы свяжемся с вами для подтверждения.\n"
        "Оплата: заглушка (интеграцию платежей добавим позже)."
    )
    await state.clear()
