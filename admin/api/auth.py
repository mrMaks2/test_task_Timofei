import hmac
import hashlib
import json
from django.conf import settings

def validate_telegram_init_data(init_data: str) -> bool:
    """
    Полная валидация initData от Telegram WebApp
    
    Args:
        init_data: строка с данными инициализации из Telegram.WebApp.initData
    
    Returns:
        bool: True если данные валидны
    """
    try:
        from urllib.parse import parse_qs
        
        # Парсим query string
        parsed_data = parse_qs(init_data)
        
        # Извлекаем hash
        received_hash = parsed_data.get('hash', [''])[0]
        if not received_hash:
            return False
        
        # Удаляем hash из данных для проверки
        data_check_pairs = []
        for key, values in parsed_data.items():
            if key != 'hash':
                # Берем первое значение для каждого ключа
                data_check_pairs.append(f"{key}={values[0]}")
        
        # Сортируем и соединяем
        data_check_string = '\n'.join(sorted(data_check_pairs))
        
        # Создаем секретный ключ
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=settings.BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Вычисляем ожидаемый hash
        expected_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Сравниваем
        return hmac.compare_digest(expected_hash, received_hash)
        
    except Exception as e:
        print(f"Validation error: {e}")
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
        from urllib.parse import parse_qs
        import json
        
        parsed_data = parse_qs(init_data)
        user_data = parsed_data.get('user', [''])[0]
        
        if user_data:
            return json.loads(user_data)
        return None
    except Exception:
        return None