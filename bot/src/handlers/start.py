from aiogram import Router
from typing import Optional
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, InputMediaPhoto
from sqlalchemy import select
import src.database as db
from src.models import User, Product, ProductImage
from src.keyboards import phone_keyboard, main_menu_keyboard, product_keyboard
from src.config import settings

router = Router()


def _media_url(path: str) -> str:
    base = settings.MEDIA_BASE_URL.rstrip("/")
    return f"{base}/{path.lstrip('/')}"


async def _get_or_create_user(message: Message, db_user: Optional[User]) -> Optional[User]:
    if db_user:
        return db_user
    if not db.async_session_maker or not message.from_user:
        return None
    async with db.async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
            )
            session.add(user)
            await session.commit()
        return user


async def send_product(message: Message, product_id: int) -> None:
    if not db.async_session_maker:
        return
    async with db.async_session_maker() as session:
        result = await session.execute(
            select(Product).where(Product.id == product_id, Product.is_active == True)
        )
        product = result.scalar_one_or_none()
        if not product:
            await message.answer("Товар не найден.")
            return
        images_result = await session.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product.id)
            .order_by(ProductImage.order)
        )
        images = images_result.scalars().all()

    if images:
        media = [
            InputMediaPhoto(
                media=_media_url(img.image),
                caption=product.name if i == 0 else None,
            )
            for i, img in enumerate(images)
        ]
        await message.answer_media_group(media)

    await message.answer(
        f"<b>{product.name}</b>\n{product.description}\nЦена: {product.price} руб.",
        reply_markup=product_keyboard(product.id),
    )


@router.message(CommandStart())
async def cmd_start(message: Message, db_user: Optional[User] = None):
    db_user = await _get_or_create_user(message, db_user)
    if not db_user:
        await message.answer("Ошибка инициализации пользователя. Попробуйте позже.")
        return
    payload = ""
    if message.text and " " in message.text:
        payload = message.text.split(" ", 1)[1].strip()

    if payload.startswith("product_"):
        try:
            product_id = int(payload.split("_", 1)[1])
            await send_product(message, product_id)
            return
        except ValueError:
            pass

    if not db_user.phone:
        await message.answer(
            "Добро пожаловать! Поделитесь номером телефона для регистрации.",
            reply_markup=phone_keyboard(),
        )
    else:
        await message.answer(
            f"С возвращением, {db_user.first_name or 'пользователь'}!",
            reply_markup=main_menu_keyboard(),
        )


@router.message(lambda msg: msg.contact is not None)
async def handle_contact(message: Message, db_user: Optional[User] = None):
    db_user = await _get_or_create_user(message, db_user)
    if not db_user:
        await message.answer("Ошибка инициализации пользователя. Попробуйте позже.")
        return
    if not db.async_session_maker:
        return
    async with db.async_session_maker() as session:
        db_user.phone = message.contact.phone_number
        session.add(db_user)
        await session.commit()
    await message.answer(
        "Спасибо! Теперь вы можете пользоваться ботом.",
        reply_markup=main_menu_keyboard(),
    )
    await message.answer(
        "Клавиатура скрыта.",
        reply_markup=ReplyKeyboardRemove(),
    )
