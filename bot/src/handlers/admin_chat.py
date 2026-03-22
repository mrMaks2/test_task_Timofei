from aiogram import Router, types, F
from sqlalchemy import select
import src.database as db
from src.models import Order, User

router = Router()


@router.callback_query(F.data.startswith("order_status:"))
async def change_order_status(callback: types.CallbackQuery):
    _, order_id, new_status = callback.data.split(":")
    order_id = int(order_id)
    async with db.async_session_maker() as session:
        order = await session.get(Order, order_id)
        if not order:
            await callback.answer("Заказ не найден.")
            return
        order.status = new_status
        await session.commit()

        user = await session.get(User, order.user_id)
        if user:
            await callback.bot.send_message(
                user.telegram_id,
                f"Статус вашего заказа #{order.id} изменен на: {new_status}",
            )

    await callback.message.edit_text(
        f"Статус заказа #{order_id} изменен на {new_status}.",
        reply_markup=None,
    )
    await callback.answer("Статус обновлен")
