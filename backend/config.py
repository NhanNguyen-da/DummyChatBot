"""
Config.py - File cấu hình cho ứng dụng
Chứa các thiết lập về database, API, và các biến môi trường
"""

import os
from pathlib import Path

# Đường dẫn gốc của project
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """
    Class chứa các cấu hình cơ bản cho ứng dụng
    """

    # Cấu hình Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True

    # === SQL Server 2020 Configuration ===
    DB_CONFIG = {
        'server': 'localhost',                    # hoặc 'localhost\\SQLEXPRESS' nếu dùng Express
        'database': 'chatbot',
        'driver': 'ODBC Driver 17 for SQL Server',
        'username': 'nt',
        'password': 'Ntn@1997',
        'trusted_connection': False,              # Set True for Windows Authentication
    }
    # Cấu hình CORS (cho phép Angular frontend truy cập)
    CORS_ORIGINS = [
        "http://localhost:4200",  # Angular development server
        "http://127.0.0.1:4200"
    ]

    # Cấu hình API
    API_PREFIX = '/api/v1'

    # Cấu hình LLM - UPDATED 
    LLM_MODEL_NAME = 'Qwen3-4B-Instruct-2507'
    LLM_MODEL_PATH = None

    # Cấu hình Chatbot
    MAX_CONVERSATION_HISTORY = 10  # Số lượng tin nhắn tối đa lưu trong lịch sử
    SESSION_TIMEOUT = 3600  # Timeout session (giây)

# Module-level configuration for easy access
FLASK_HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

# Ollama configuration - FIXED 
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen3:4b-instruct-2507-q4_k_m')  
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')

# Export Config class attributes as module-level
SECRET_KEY = Config.SECRET_KEY
DB_CONFIG = Config.DB_CONFIG
CORS_ORIGINS = Config.CORS_ORIGINS
API_PREFIX = Config.API_PREFIX
LLM_MODEL_NAME = Config.LLM_MODEL_NAME
LLM_MODEL_PATH = Config.LLM_MODEL_PATH
MAX_CONVERSATION_HISTORY = Config.MAX_CONVERSATION_HISTORY
SESSION_TIMEOUT = Config.SESSION_TIMEOUT

class DevelopmentConfig(Config):
    """Cấu hình cho môi trường Development"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Cấu hình cho môi trường Production"""
    DEBUG = False
    TESTING = False
    # TODO: Thêm các cấu hình production khác

# Dictionary để chọn config dựa vào môi trường
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}   