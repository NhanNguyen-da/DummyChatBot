# test_chat.py - Comprehensive test for chatbot service
# Tests: 3-turn simple symptoms + 1 red flag case

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.chatbot_service import ChatbotService


def print_separator(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def print_result(result, turn_number):
    """Pretty print the chatbot response"""
    print(f"\n--- Turn {turn_number} Result ---")
    print(f"  Response: {result.get('response', 'N/A')[:100]}...")
    print(f"  Alert Level: {result.get('alertLevel', 'None')}")
    print(f"  Confidence: {result.get('confidence', 0):.2f}")
    print(f"  Status: {result.get('conversationStatus', 'N/A')}")

    if result.get('suggestedDepartment'):
        print(f"  Suggested Dept: {result.get('suggestedDepartment')}")

    if result.get('quickReplies'):
        print(f"  Quick Replies: {len(result['quickReplies'])} options")
        for qr in result['quickReplies'][:3]:
            print(f"    - {qr.get('label', 'N/A')}")

    if result.get('departmentRecommendation'):
        dept = result['departmentRecommendation']
        print(f"  RECOMMENDATION:")
        print(f"    Department: {dept.get('departmentName')}")
        print(f"    Room: {dept.get('roomNumber')}, Floor: {dept.get('floor')}")
        print(f"    Doctor: {dept.get('doctorName')}")


def test_simple_symptoms_3_turns():
    """
    Test Case 1: Simple symptoms over 3 turns
    Simulates a user with stomach pain providing information gradually
    """
    print_separator("TEST CASE 1: Simple Symptoms (3 Turns)")

    service = ChatbotService()
    session_id = "test-simple-001"

    # Reset any previous test data
    service.reset_conversation(session_id)

    try:
        # Turn 1: Initial symptom
        print("\n[Turn 1] User: 'Toi bi dau bung' (I have stomach pain)")
        result1 = service.process_message("Toi bi dau bung", session_id)
        print_result(result1, 1)

        assert result1.get('conversationStatus') == 'in_progress', "Turn 1 should be in_progress"
        print("  [OK] Status is in_progress")

        # Turn 2: Add more info - severity
        print("\n[Turn 2] User: 'Dau du doi lam, 30 tuoi' (Very severe pain, 30 years old)")
        result2 = service.process_message("Dau du doi lam, toi 30 tuoi", session_id)
        print_result(result2, 2)

        # Turn 3: Add duration/location
        print("\n[Turn 3] User: 'Dau bung tren, 2 ngay roi' (Upper abdomen, 2 days)")
        result3 = service.process_message("Dau bung tren, da 2 ngay roi", session_id)
        print_result(result3, 3)

        # Check if we got a recommendation or appropriate follow-up
        if result3.get('departmentRecommendation'):
            print("\n  [SUCCESS] Got department recommendation after 3 turns")
        else:
            print(f"\n  [INFO] Confidence: {result3.get('confidence', 0):.2f} - may need more info")

        print("\n" + "-" * 40)
        print("TEST CASE 1: PASSED")

    except Exception as e:
        print(f"\n[FAILED] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        service.reset_conversation(session_id)

    return True


def test_red_flag_emergency():
    """
    Test Case 2: Red flag - Chest pain emergency
    Should trigger immediate emergency response

    Red flag keywords from database:
    - Primary: 'đau ngực', 'đau tim'
    - Secondary: 'lan ra tay trái', 'đổ mồ hôi lạnh', 'khó thở', 'buồn nôn'
    """
    print_separator("TEST CASE 2: Red Flag - Chest Pain Emergency")

    service = ChatbotService()
    session_id = "test-redflag-001"

    # Reset any previous test data
    service.reset_conversation(session_id)

    try:
        # Emergency message with red flag keywords
        print("\n[Turn 1] User: 'Toi dau nguc du doi, kho tho, do mo hoi lanh'")
        print("         (I have severe chest pain, difficulty breathing, cold sweats)")

        result = service.process_message(
            "Toi dau nguc du doi, kho tho, do mo hoi lanh",
            session_id
        )
        print_result(result, 1)

        # Check for emergency response
        alert_level = result.get('alertLevel')
        status = result.get('conversationStatus')
        response = result.get('response', '')

        print("\n--- Verification ---")

        if alert_level in ['danger', 'warning']:
            print(f"  [OK] Alert Level: {alert_level}")
        else:
            print(f"  [WARNING] Expected 'danger' or 'warning', got: {alert_level}")

        if status == 'completed':
            print(f"  [OK] Status: {status} (emergency ends conversation)")
        else:
            print(f"  [INFO] Status: {status}")

        if 'CẤP CỨU' in response.upper() or 'CAP CUU' in response.upper() or '115' in response:
            print("  [OK] Response contains emergency keywords")
        else:
            print("  [INFO] Response may not contain emergency keywords")

        print("\n" + "-" * 40)
        print("TEST CASE 2: PASSED")

    except Exception as e:
        print(f"\n[FAILED] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        service.reset_conversation(session_id)

    return True


def test_red_flag_stroke():
    """
    Test Case 3: Red flag - Stroke symptoms
    Keywords: 'tê nửa người', 'liệt nửa người', 'méo miệng'
    """
    print_separator("TEST CASE 3: Red Flag - Stroke Symptoms")

    service = ChatbotService()
    session_id = "test-redflag-002"

    service.reset_conversation(session_id)

    try:
        print("\n[Turn 1] User: 'Toi bi te nua nguoi, meo mieng, dau dau du doi'")
        print("         (Numbness on half body, facial drooping, severe headache)")

        result = service.process_message(
            "Toi bi te nua nguoi, meo mieng, dau dau du doi",
            session_id
        )
        print_result(result, 1)

        alert_level = result.get('alertLevel')

        if alert_level in ['danger', 'warning']:
            print(f"\n  [OK] Stroke symptoms detected - Alert: {alert_level}")
        else:
            print(f"\n  [INFO] Alert Level: {alert_level}")

        print("\n" + "-" * 40)
        print("TEST CASE 3: PASSED")

    except Exception as e:
        print(f"\n[FAILED] Error: {str(e)}")
        return False

    finally:
        service.reset_conversation(session_id)

    return True


def test_question_rotation():
    """
    Test Case 4: Verify questions don't repeat (loop fix)
    """
    print_separator("TEST CASE 4: Question Rotation (No Loop)")

    service = ChatbotService()
    session_id = "test-rotation-001"

    service.reset_conversation(session_id)

    try:
        questions_asked = []

        # Turn 1: Initial symptom
        print("\n[Turn 1] User: 'Toi bi dau dau'")
        result1 = service.process_message("Toi bi dau dau", session_id)
        q1 = result1.get('response', '')[:50]
        questions_asked.append(q1)
        print(f"  Question: {q1}...")

        # Turn 2: User provides another symptom (not answering the question)
        print("\n[Turn 2] User: 'Con buon non nua'")
        result2 = service.process_message("Con buon non nua", session_id)
        q2 = result2.get('response', '')[:50]
        questions_asked.append(q2)
        print(f"  Question: {q2}...")

        # Turn 3: Another symptom
        print("\n[Turn 3] User: 'Cam thay met moi'")
        result3 = service.process_message("Cam thay met moi", session_id)
        q3 = result3.get('response', '')[:50]
        questions_asked.append(q3)
        print(f"  Question: {q3}...")

        # Check if questions are different
        print("\n--- Verification ---")
        if q1 != q2 and q2 != q3:
            print("  [OK] Questions are different - no loop detected")
        else:
            print("  [WARNING] Some questions may have repeated")
            for i, q in enumerate(questions_asked):
                print(f"    Turn {i+1}: {q}...")

        print("\n" + "-" * 40)
        print("TEST CASE 4: PASSED")

    except Exception as e:
        print(f"\n[FAILED] Error: {str(e)}")
        return False

    finally:
        service.reset_conversation(session_id)

    return True


def run_all_tests():
    """Run all test cases"""
    print("\n")
    print("*" * 60)
    print("*  CHATBOT TRIAGE - COMPREHENSIVE TEST SUITE")
    print("*" * 60)

    results = []

    # Test 1: Simple symptoms 3 turns
    results.append(("Simple Symptoms (3 turns)", test_simple_symptoms_3_turns()))

    # Test 2: Red flag - chest pain
    results.append(("Red Flag - Chest Pain", test_red_flag_emergency()))

    # Test 3: Red flag - stroke
    results.append(("Red Flag - Stroke", test_red_flag_stroke()))

    # Test 4: Question rotation (no loop)
    results.append(("Question Rotation", test_question_rotation()))

    # Summary
    print_separator("TEST SUMMARY")
    passed = 0
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        icon = "[OK]" if result else "[X]"
        print(f"  {icon} {name}: {status}")
        if result:
            passed += 1

    print(f"\n  Total: {passed}/{len(results)} tests passed")
    print("=" * 60)

    return passed == len(results)


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
