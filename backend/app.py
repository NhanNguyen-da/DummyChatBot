# backend/app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import config
import sys
import traceback

# Khởi tạo Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, origins=config.CORS_ORIGINS)

# Root route - để test xem server có chạy không
@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint
    """
    return jsonify({
        'message': 'Chatbot Triage API',
        'version': '1.0',
        'endpoints': {
            'health': '/api/health',
            'test_ollama': '/api/test-ollama'
        }
    })

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint để check xem server có đang chạy không
    """
    return jsonify({
        'status': 'ok',
        'message': 'Chatbot Triage API is running'
    })

# Test Ollama endpoint
@app.route('/api/test-ollama', methods=['GET'])
def test_ollama():
    """
    Endpoint để test xem Ollama có connect được không
    """
    try:
        import ollama
        
        print("🤖 Testing Ollama connection...")
        print(f"📦 Using model: {config.OLLAMA_MODEL}")
        
        # Test simple generation
        response = ollama.chat(
            model=config.OLLAMA_MODEL,
            messages=[
                {'role': 'user', 'content': 'Xin chào, trả lời ngắn gọn bằng tiếng Việt.'}
            ]
        )
        
        print("✅ Ollama test successful!")
        
        return jsonify({
            'status': 'ok',
            'message': 'Ollama is working',
            'model': config.OLLAMA_MODEL,
            'test_response': response['message']['content']
        })
    
    except Exception as e:
        print("❌ Ollama test failed!")
        print(f"Error: {str(e)}")
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': f'Ollama connection failed: {str(e)}'
        }), 500

# Error handler cho 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint không tồn tại',
        'message': 'Vui lòng kiểm tra lại URL'
    }), 404

# Error handler cho 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': str(error)
    }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Server đang chạy ở môi trường: development")
    print(f"📍 Truy cập tại: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"🤖 Ollama Model: {config.OLLAMA_MODEL}")
    print(f"💾 Database: {config.DATABASE_PATH}")
    print("=" * 60)
    print("\n📋 Available Endpoints:")
    print(f"  GET  /                    - API Info")
    print(f"  GET  /api/health          - Health Check")
    print(f"  GET  /api/test-ollama     - Test Ollama Connection")
    print("=" * 60)
    print("\n✨ Server is ready! Press CTRL+C to quit\n")
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )