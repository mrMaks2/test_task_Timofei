from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from ..database import async_session_maker
from ..models import Order

router = Router()

@router.callback_query(F.data.startswith('order_status:'))
async def change_order_status(callback: types.CallbackQuery):
    _, order_id, new_status = callback.data.split(':')
    order_id = int(order_id)
    async with async_session_maker() as session:
        order = await session.get(Order, order_id)
        if order:
            order.status = new_status
            await session.commit()
            await callback.message.edit_text(
                f"Статус заказа #{order.id} изменён на {new_status}.",
                reply_markup=None
            )
            # Уведомление пользователю (через бота, но здесь просто ответ)
    await callback.answer("Статус обновлён")