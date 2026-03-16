import hmac
import hashlib
import json
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from apps.catalog.models import Category, Product
from apps.customers.models import Customer
from apps.orders.models import Order, OrderItem
from apps.cart.models import Cart, CartItem
import requests
from urllib.parse import parse_qs
import logging

logger = logging.getLogger(__name__)

def validate_telegram_init_data(init_data: str) -> bool:
    """
    Валидация данных инициализации от Telegram WebApp
    """
    try:
        # Парсим initData
        data_pairs = {}
        for pair in init_data.split('&'):
            key, value = pair.split('=')
            data_pairs[key] = value
        
        # Проверяем наличие hash
        if 'hash' not in data_pairs:
            return False
        
        received_hash = data_pairs['hash']
        data_check_string = '\n'.join(
            f"{k}={v}" for k, v in sorted(data_pairs.items()) if k != 'hash'
        )
        
        # Вычисляем ожидаемый hash
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=settings.BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        expected_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_hash, received_hash)
    except Exception:
        return False

def get_user_from_init_data(init_data: str):
    """
    Извлекает пользователя из initData
    
    Args:
        init_data: строка с данными инициализации
    
    Returns:
        dict: данные пользователя или None
    """
    try:
        parsed_data = parse_qs(init_data)
        user_data = parsed_data.get('user', [''])[0]
        
        if user_data:
            # Декодируем URL-encoded JSON
            import urllib.parse
            user_data = urllib.parse.unquote(user_data)
            return json.loads(user_data)
        return None
    except Exception as e:
        logger.error(f"Error extracting user from init_data: {e}")
        return None

@api_view(['POST'])
def validate_init_data(request):
    """
    Эндпоинт для валидации init_data от Telegram WebApp
    """
    init_data = request.data.get('init_data')
    if not init_data:
        return Response(
            {'valid': False, 'error': 'init_data is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    bot_token = settings.BOT_TOKEN
    is_valid = validate_telegram_init_data(init_data, bot_token)
    
    if is_valid:
        user_data = get_user_from_init_data(init_data)
        return Response({
            'valid': True,
            'user': user_data
        })
    else:
        return Response({'valid': False})

class ValidateInitDataView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        init_data = request.data.get('init_data')
        if not init_data:
            return Response({'valid': False}, status=status.HTTP_400_BAD_REQUEST)
        
        is_valid = validate_telegram_init_data(init_data)
        return Response({'valid': is_valid})

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра категорий
    """
    queryset = Category.objects.filter(is_active=True).order_by('order')
    serializer_class = CategorySerializer
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        category = self.get_object()
        products = Product.objects.filter(category=category, is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet для просмотра товаров
    """
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

class CartViewSet(viewsets.GenericViewSet):
    """
    ViewSet для работы с корзиной
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_cart(self, request):
        # Получаем или создаем корзину для пользователя
        # В реальном проекте нужно получать пользователя из initData
        telegram_id = request.headers.get('X-Telegram-Id')
        if telegram_id:
            customer, _ = Customer.objects.get_or_create(telegram_id=telegram_id)
            cart, _ = Cart.objects.get_or_create(user=customer)
            return cart
        return None
    
    def list(self, request):
        cart = self.get_cart(request)
        if not cart:
            return Response({'items': [], 'total_amount': 0})
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_cart(request)
        if not cart:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        try:
            cart_item = CartItem.objects.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        serializer = CartSerializer(cart_item.cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        item_id = request.data.get('item_id')
        
        try:
            cart_item = CartItem.objects.get(id=item_id)
            cart = cart_item.cart
            cart_item.delete()
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_cart(request)
        if cart:
            cart.items.all().delete()
        return Response({'status': 'cart cleared'})

class OrderViewSet(viewsets.GenericViewSet):
    """
    ViewSet для работы с заказами
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_customer(self, request):
        telegram_id = request.headers.get('X-Telegram-Id')
        if telegram_id:
            return Customer.objects.filter(telegram_id=telegram_id).first()
        return None
    
    def list(self, request):
        customer = self.get_customer(request)
        if not customer:
            return Response([])
        
        orders = Order.objects.filter(user=customer).order_by('-created_at')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        customer = self.get_customer(request)
        if not customer:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Получаем корзину
        try:
            cart = Cart.objects.get(user=customer)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_items = cart.items.all()
        if not cart_items:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Создаем заказ
        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        order = Order.objects.create(
            user=customer,
            full_name=serializer.validated_data['full_name'],
            address=serializer.validated_data['address'],
            phone=serializer.validated_data.get('phone', customer.phone),
            total=total,
            status='new'
        )
        
        # Создаем позиции заказа
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        # Очищаем корзину
        cart.items.all().delete()
        
        # Отправляем уведомление в админ-чат
        self.notify_admin(order)
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    
    def notify_admin(self, order):
        """
        Отправка уведомления о новом заказе в админ-чат
        """
        try:
            from apps.bot_settings.models import Setting
            admin_chat_id = Setting.objects.get(key='admin_chat_id').value
        except (Setting.DoesNotExist, Exception):
            admin_chat_id = settings.ADMIN_CHAT_ID
        
        if admin_chat_id and settings.BOT_INTERNAL_TOKEN:
            message = (
                f"🆕 <b>Новый заказ #{order.id}</b>\n\n"
                f"👤 {order.full_name}\n"
                f"📞 {order.phone}\n"
                f"📍 {order.address}\n"
                f"💰 Сумма: {order.total} руб.\n\n"
                f"📦 Товары:\n"
            )
            
            for item in order.items.all():
                message += f"  • {item.product.name} x{item.quantity} = {item.price * item.quantity} руб.\n"
            
            # Отправляем уведомление боту
            requests.post(
                settings.BOT_WEBHOOK_URL,
                json={
                    'event': 'new_order',
                    'chat_id': admin_chat_id,
                    'message': message,
                    'order_id': order.id
                },
                headers={'Authorization': f'Bearer {settings.BOT_INTERNAL_TOKEN}'}
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        
        # Проверяем, что заказ принадлежит пользователю
        customer = self.get_customer(request)
        if not customer or order.user != customer:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if order.status in ['new', 'paid']:
            order.status = 'cancelled'
            order.save()
            return Response({'status': 'order cancelled'})
        else:
            return Response({'error': 'Cannot cancel order in current status'}, 
                          status=status.HTTP_400_BAD_REQUEST)