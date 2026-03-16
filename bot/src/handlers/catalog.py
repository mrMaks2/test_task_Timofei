from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from ..database import async_session_maker
from ..models import Category, Product, ProductImage
from ..keyboards import product_keyboard

router = Router()

@router.callback_query(F.data == 'catalog')
async def show_categories(callback: types.CallbackQuery):
    async with async_session_maker() as session:
        categories = await session.execute(
            select(Category).where(Category.parent_id.is_(None), Category.is_active).order_by(Category.order)
        )
        categories = categories.scalars().all()
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=cat.name, callback_data=f"cat_{cat.id}")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(1)
    await callback.message.edit_text("Выберите категорию:", reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith('cat_'))
async def open_category(callback: types.CallbackQuery):
    cat_id = int(callback.data.split('_')[1])
    async with async_session_maker() as session:
        # Проверяем подкатегории
        subcats = await session.execute(
            select(Category).where(Category.parent_id == cat_id, Category.is_active)
        )
        subcats = subcats.scalars().all()
        if subcats:
            builder = InlineKeyboardBuilder()
            for sub in subcats:
                builder.button(text=sub.name, callback_data=f"cat_{sub.id}")
            builder.button(text="🔙 Назад", callback_data="catalog")
            builder.adjust(1)
            await callback.message.edit_text("Подкатегории:", reply_markup=builder.as_markup())
        else:
            # Товары категории
            products = await session.execute(
                select(Product).where(Product.category_id == cat_id, Product.is_active)
            )
            products = products.scalars().all()
            if not products:
                await callback.answer("В этой категории пока нет товаров.")
                return
            for product in products:
                images = await session.execute(
                    select(ProductImage).where(ProductImage.product_id == product.id).order_by(ProductImage.order)
                )
                images = images.scalars().all()
                # Отправка медиагруппы
                if images:
                    media = []
                    # формируем InputMediaPhoto
                    # ... (опущено для краткости)
                    await callback.message.answer_media_group(media)
                await callback.message.answer(
                    f"<b>{product.name}</b>\n{product.description}\nЦена: {product.price} руб.",
                    reply_markup=product_keyboard(product.id)
                )
            await callback.message.answer("Выберите товар или вернитесь в каталог.")