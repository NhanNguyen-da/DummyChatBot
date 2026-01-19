"""
validators.py - Các hàm validation
"""

import re

def is_valid_session_id(session_id):
    """
    Kiểm tra session_id có hợp lệ không (UUID format)

    Args:
        session_id (str): Session ID cần kiểm tra

    Returns:
        bool: True nếu hợp lệ
    """
    uuid_pattern = re.compile(
        r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(str(session_id)))

def sanitize_input(user_input):
    """
    Làm sạch và sanitize input từ người dùng để tránh injection

    Args:
        user_input (str): Input từ người dùng

    Returns:
        str: Input đã được sanitize
    """
    if not user_input:
        return ""

    # Loại bỏ các ký tự đặc biệt nguy hiểm
    # Chỉ giữ lại chữ, số, dấu câu cơ bản và tiếng Việt
    sanitized = re.sub(r'[<>{}[\]\\]', '', user_input)

    return sanitized.strip()
