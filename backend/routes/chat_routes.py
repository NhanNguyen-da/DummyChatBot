"""
chat_routes.py - Routes xử lý chat với người dùng
Chứa các endpoint cho tương tác chatbot
"""

from flask import Blueprint, request, jsonify

# Tạo Blueprint cho chat routes
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint xử lý tin nhắn từ người dùng

    Request body:
    {
        "message": "Tôi bị đau đầu",
        "session_id": "uuid-string",
        "conversation_history": []
    }

    Returns:
        JSON response với câu trả lời của bot
    """
    # TODO: Implement chat logic
    data = request.get_json()

    return jsonify({
        'response': 'Xin chào! Tôi là trợ lý y tế. Hãy cho tôi biết triệu chứng của bạn.',
        'session_id': data.get('session_id'),
        'suggested_department': None
    }), 200

@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """
    Lấy lịch sử hội thoại của một session

    Args:
        session_id (str): ID của session

    Returns:
        JSON response với lịch sử hội thoại
    """
    # TODO: Implement get history from database
    return jsonify({
        'session_id': session_id,
        'history': []
    }), 200

@chat_bp.route('/chat/reset', methods=['POST'])
def reset_chat():
    """
    Reset cuộc hội thoại, bắt đầu lại từ đầu

    Request body:
    {
        "session_id": "uuid-string"
    }

    Returns:
        JSON response xác nhận reset thành công
    """
    # TODO: Implement reset logic
    data = request.get_json()

    return jsonify({
        'message': 'Đã reset cuộc hội thoại',
        'session_id': data.get('session_id')
    }), 200
