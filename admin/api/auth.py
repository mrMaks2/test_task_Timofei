import hmac
import hashlib
import json
from urllib.parse import parse_qs
from django.conf import settings


def validate_telegram_init_data(init_data: str) -> bool:
    """
    Validate initData from Telegram WebApp.
    """
    try:
        parsed_data = parse_qs(init_data, strict_parsing=True)
        received_hash = parsed_data.get("hash", [""])[0]
        if not received_hash:
            return False

        data_check_pairs = []
        for key, values in parsed_data.items():
            if key != "hash":
                data_check_pairs.append(f"{key}={values[0]}")

        data_check_string = "\n".join(sorted(data_check_pairs))

        secret_key = hmac.new(
            key=b"WebAppData",
            msg=settings.BOT_TOKEN.encode(),
            digestmod=hashlib.sha256,
        ).digest()

        expected_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected_hash, received_hash)
    except Exception:
        return False


def get_user_from_init_data(init_data: str):
    """
    Extract user info from initData.
    """
    try:
        parsed_data = parse_qs(init_data)
        user_data = parsed_data.get("user", [""])[0]
        if user_data:
            return json.loads(user_data)
        return None
    except Exception:
        return None
