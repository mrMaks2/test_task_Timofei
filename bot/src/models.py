from sqlalchemy import (
    Column, Integer, String, BigInteger, Boolean, DateTime,
    ForeignKey, Text, Float, JSON
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'customers_customer'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(150), nullable=True)
    phone = Column(String(20), nullable=True)
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")

class Category(Base):
    __tablename__ = 'catalog_category'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('catalog_category.id'), nullable=True)
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)

    parent = relationship("Category", remote_side=[id], backref="children")

class Product(Base):
    __tablename__ = 'catalog_product'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('catalog_category.id'), nullable=False)
    name = Column(String(300), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category")
    images = relationship("ProductImage", back_populates="product")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")

class ProductImage(Base):
    __tablename__ = 'catalog_productimage'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('catalog_product.id'), nullable=False)
    image = Column(String(500))
    order = Column(Integer, default=0)

    product = relationship("Product", back_populates="images")

class Cart(Base):
    __tablename__ = 'cart_cart'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customers_customer.id'), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = 'cart_cartitem'
    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('cart_cart.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('catalog_product.id'), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

class Order(Base):
    __tablename__ = 'orders_order'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('customers_customer.id'), nullable=False)
    status = Column(String(50), default='new')
    full_name = Column(String(300))
    address = Column(Text)
    phone = Column(String(20))
    total = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'orders_orderitem'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders_order.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('catalog_product.id'), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

class FAQ(Base):
    __tablename__ = 'faq_faq'
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)

class Channel(Base):
    __tablename__ = 'bot_settings_channel'
    id = Column(Integer, primary_key=True)
    chat_id = Column(String(200), nullable=False, unique=True)
    title = Column(String(300))
    is_mandatory = Column(Boolean, default=True)

class Mailing(Base):
    __tablename__ = 'mailing_mailing'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    image = Column(String(500), nullable=True)
    status = Column(String(50), default='draft')
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

class MailingLog(Base):
    __tablename__ = 'mailing_mailinglog'
    id = Column(Integer, primary_key=True)
    mailing_id = Column(Integer, ForeignKey('mailing_mailing.id'))
    user_id = Column(Integer, ForeignKey('customers_customer.id'))
    status = Column(String(50))
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)