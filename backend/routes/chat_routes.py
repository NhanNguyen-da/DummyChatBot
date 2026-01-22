"""
chat_routes.py - Routes xử lý chat với người dùng
Chứa các endpoint cho tương tác chatbot
"""

from flask import Blueprint, request, jsonify
from services.chatbot_service import ChatbotService

# Tạo Blueprint cho chat routes
chat_bp = Blueprint('chat', __name__)

# Initialize chatbot service
chatbot_service = ChatbotService()


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint xử lý tin nhắn từ người dùng

    Request body:
    {
        "message": "Tôi bị đau đầu",
        "sessionId": "uuid-string"
    }

    Returns:
        JSON response với câu trả lời của bot
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'error': 'Request body is required'
            }), 400

        message = data.get('message', '').strip()
        session_id = data.get('sessionId')

        if not message:
            return jsonify({
                'error': 'Message is required'
            }), 400

        if not session_id:
            return jsonify({
                'error': 'Session ID is required'
            }), 400

        # Process message through triage service
        result = chatbot_service.process_message(message, session_id)

        return jsonify(result), 200

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """
    Lấy lịch sử hội thoại của một session

    Args:
        session_id (str): ID của session

    Returns:
        JSON response với lịch sử hội thoại
    """
    try:
        if not session_id:
            return jsonify({
                'error': 'Session ID is required'
            }), 400

        history = chatbot_service.get_conversation_history(session_id)

        # Format history for frontend
        formatted_history = []
        for turn in history:
            if turn['user_message']:
                formatted_history.append({
                    'type': 'user',
                    'text': turn['user_message'],
                    'timestamp': turn['timestamp']
                })
            if turn['bot_response']:
                formatted_history.append({
                    'type': 'bot',
                    'text': turn['bot_response'],
                    'timestamp': turn['timestamp']
                })

        return jsonify({
            'sessionId': session_id,
            'history': formatted_history
        }), 200

    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@chat_bp.route('/chat/reset', methods=['POST'])
def reset_chat():
    """
    Reset cuộc hội thoại, bắt đầu lại từ đầu

    Request body:
    {
        "sessionId": "uuid-string"
    }

    Returns:
        JSON response xác nhận reset thành công
    """
    try:
        data = request.get_json()
        session_id = data.get('sessionId')

        if not session_id:
            return jsonify({
                'error': 'Session ID is required'
            }), 400

        chatbot_service.reset_conversation(session_id)

        return jsonify({
            'message': 'Đã reset cuộc hội thoại',
            'sessionId': session_id
        }), 200

    except Exception as e:
        print(f"Error resetting chat: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500
