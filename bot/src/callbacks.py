from aiogram.filters.callback_data import CallbackData


class CatalogRootCb(CallbackData, prefix="catalog"):
    page: int = 1


class CategoryCb(CallbackData, prefix="cat"):
    id: int
    page: int = 1


class ProductCb(CallbackData, prefix="product"):
    id: int


class CartItemCb(CallbackData, prefix="cart_item"):
    id: int


class CartActionCb(CallbackData, prefix="cart_action"):
    action: str
    item_id: int = 0
