# test_chat.py - Test the chatbot service directly

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.chatbot_service import ChatbotService

def test_chat_service():
    """Test the chatbot service directly"""
    print("=" * 50)
    print("Testing ChatbotService")
    print("=" * 50)

    try:
        # Initialize service
        print("\n1. Initializing ChatbotService...")
        service = ChatbotService()
        print("   OK")

        # Generate test session ID
        session_id = "test-session-001"

        # Test message
        test_message = "Toi bi dau dau"

        print(f"\n2. Processing message: '{test_message}'")
        print(f"   Session ID: {session_id}")

        result = service.process_message(test_message, session_id)

        print("\n3. Result:")
        print(f"   Response: {result.get('response', 'N/A')}")
        print(f"   Alert Level: {result.get('alertLevel', 'None')}")
        print(f"   Suggested Dept: {result.get('suggestedDepartment', 'None')}")
        print(f"   Status: {result.get('conversationStatus', 'N/A')}")

        if result.get('quickReplies'):
            print(f"   Quick Replies: {len(result['quickReplies'])} options")

        if result.get('departmentRecommendation'):
            print(f"   Department: {result['departmentRecommendation'].get('departmentName')}")

        print("\n" + "=" * 50)
        print("SUCCESS: Chat service is working!")
        print("=" * 50)

        # Cleanup - reset test session
        print("\n4. Cleaning up test session...")
        service.reset_conversation(session_id)
        print("   Done")

        return True

    except Exception as e:
        print(f"\nFAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_chat_service()
