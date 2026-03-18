from aiogram import Router, types, F
from aiogram.types import InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from ..database import async_session_maker
from ..models import Category, Product, ProductImage
from ..keyboards import product_keyboard
from ..callbacks import CatalogRootCb, CategoryCb
from ..config import settings

router = Router()
PAGE_SIZE = 5


async def _send_product(callback: types.CallbackQuery, product: Product) -> None:
    async with async_session_maker() as session:
        images_result = await session.execute(
            select(ProductImage)
            .where(ProductImage.product_id == product.id)
            .order_by(ProductImage.order)
        )
        images = images_result.scalars().all()

    def _media_url(path: str) -> str:
        base = settings.MEDIA_BASE_URL.rstrip("/")
        return f"{base}/{path.lstrip('/')}"

    if images:
        media = [
            InputMediaPhoto(
                media=_media_url(img.image),
                caption=product.name if i == 0 else None,
            )
            for i, img in enumerate(images)
        ]
        await callback.message.answer_media_group(media)

    await callback.message.answer(
        f"<b>{product.name}</b>\n{product.description}\nЦена: {product.price} руб.",
        reply_markup=product_keyboard(product.id),
    )


async def _paginate(query, page: int, page_size: int):
    offset = (page - 1) * page_size
    return query.limit(page_size).offset(offset)


@router.callback_query(F.data.startswith("catalog:"))
async def show_categories(callback: types.CallbackQuery):
    data = CatalogRootCb.unpack(callback.data)
    page = data.page

    async with async_session_maker() as session:
        result = await session.execute(
            select(Category)
            .where(Category.parent_id.is_(None), Category.is_active == True)
            .order_by(Category.order)
        )
        categories = result.scalars().all()

    if not categories:
        await callback.message.edit_text("Каталог пока пуст.")
        return

    start = (page - 1) * PAGE_SIZE
    page_items = categories[start : start + PAGE_SIZE]

    builder = InlineKeyboardBuilder()
    for cat in page_items:
        builder.button(text=cat.name, callback_data=CategoryCb(id=cat.id, page=1).pack())

    if page > 1:
        builder.button(text="Назад", callback_data=CatalogRootCb(page=page - 1).pack())
    if start + PAGE_SIZE < len(categories):
        builder.button(text="Вперед", callback_data=CatalogRootCb(page=page + 1).pack())
    builder.button(text="Главное меню", callback_data="main_menu")
    builder.adjust(1)
    await callback.message.edit_text("Выберите категорию:", reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("cat:"))
async def open_category(callback: types.CallbackQuery):
    data = CategoryCb.unpack(callback.data)
    cat_id = data.id
    page = data.page

    async with async_session_maker() as session:
        subcats_result = await session.execute(
            select(Category).where(Category.parent_id == cat_id, Category.is_active == True)
        )
        subcats = subcats_result.scalars().all()

        if subcats:
            start = (page - 1) * PAGE_SIZE
            page_items = subcats[start : start + PAGE_SIZE]
            builder = InlineKeyboardBuilder()
            for sub in page_items:
                builder.button(text=sub.name, callback_data=CategoryCb(id=sub.id, page=1).pack())
            if page > 1:
                builder.button(text="Назад", callback_data=CategoryCb(id=cat_id, page=page - 1).pack())
            if start + PAGE_SIZE < len(subcats):
                builder.button(text="Вперед", callback_data=CategoryCb(id=cat_id, page=page + 1).pack())
            builder.button(text="Каталог", callback_data=CatalogRootCb(page=1).pack())
            builder.adjust(1)
            await callback.message.edit_text("Подкатегории:", reply_markup=builder.as_markup())
            return

        products_result = await session.execute(
            select(Product)
            .where(Product.category_id == cat_id, Product.is_active == True)
            .order_by(Product.created_at.desc())
        )
        products = products_result.scalars().all()

    if not products:
        await callback.answer("В этой категории пока нет товаров.")
        return

    start = (page - 1) * PAGE_SIZE
    page_items = products[start : start + PAGE_SIZE]
    for product in page_items:
        await _send_product(callback, product)

    builder = InlineKeyboardBuilder()
    if page > 1:
        builder.button(text="Назад", callback_data=CategoryCb(id=cat_id, page=page - 1).pack())
    if start + PAGE_SIZE < len(products):
        builder.button(text="Вперед", callback_data=CategoryCb(id=cat_id, page=page + 1).pack())
    builder.button(text="Каталог", callback_data=CatalogRootCb(page=1).pack())
    builder.adjust(1)
    await callback.message.answer("Навигация по товарам:", reply_markup=builder.as_markup())
