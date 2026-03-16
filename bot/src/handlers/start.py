from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from ..database import async_session_maker
from ..models import User
from ..keyboards import phone_keyboard, main_menu_keyboard

router = Router()

@router.message(Command('start'))
async def cmd_start(message: Message, db_user: User):
    if not db_user.phone:
        await message.answer(
            "Добро пожаловать! Поделитесь номером телефона для регистрации.",
            reply_markup=phone_keyboard()
        )
    else:
        await message.answer(
            f"С возвращением, {db_user.first_name or 'пользователь'}!",
            reply_markup=main_menu_keyboard()
        )

@router.message(lambda msg: msg.contact is not None)
async def handle_contact(message: Message, db_user: User):
    async with async_session_maker() as session:
        db_user.phone = message.contact.phone_number
        session.add(db_user)
        await session.commit()
    await message.answer(
        "Спасибо! Теперь вы можете пользоваться ботом.",
        reply_markup=main_menu_keyboard(),
        reply_markup_remove=ReplyKeyboardRemove()
    )