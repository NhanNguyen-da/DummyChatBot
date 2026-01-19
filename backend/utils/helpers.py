"""
helpers.py - Các hàm helper tiện ích
"""

import uuid
from datetime import datetime

def generate_session_id():
    """
    Tạo session ID duy nhất

    Returns:
        str: UUID string
    """
    return str(uuid.uuid4())

def format_timestamp(dt=None):
    """
    Format datetime thành string

    Args:
        dt (datetime): Datetime object, mặc định là thời điểm hiện tại

    Returns:
        str: Formatted timestamp
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def clean_text(text):
    """
    Làm sạch text input từ người dùng

    Args:
        text (str): Text cần làm sạch

    Returns:
        str: Text đã được làm sạch
    """
    if not text:
        return ""
    # Loại bỏ khoảng trắng thừa
    return ' '.join(text.strip().split())

def validate_message(message):
    """
    Validate tin nhắn từ người dùng

    Args:
        message (str): Tin nhắn cần validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not message or not message.strip():
        return False, "Tin nhắn không được để trống"

    if len(message) > 1000:
        return False, "Tin nhắn quá dài (tối đa 1000 ký tự)"

    return True, None
