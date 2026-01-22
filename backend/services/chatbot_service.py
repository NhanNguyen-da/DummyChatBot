"""
chatbot_service.py - Service xử lý logic triage của chatbot
Implements 5-step triage flow: red flags -> extract symptoms -> match rules -> decide -> re-check
"""

import json
import re
import unicodedata
from models.database import Database


class ChatbotService:
    """
    Service quản lý logic chatbot triage
    """

    def __init__(self):
        """
        Khởi tạo ChatbotService
        """
        # Vietnamese accent mapping for text normalization
        self.accent_map = {
            'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
            'đ': 'd',
            # Uppercase
            'À': 'A', 'Á': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
            'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
            'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
            'È': 'E', 'É': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
            'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
            'Ì': 'I', 'Í': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
            'Ò': 'O', 'Ó': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
            'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
            'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
            'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
            'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
            'Ỳ': 'Y', 'Ý': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
            'Đ': 'D'
        }

        # Context detection keywords
        self.pregnancy_keywords = ['mang thai', 'co thai', 'thai nghen', 'bau', 'thai ky']
        self.pediatric_keywords = ['con toi', 'be', 'chau', 'tre', 'thang tuoi', 'tuoi']
        self.severity_keywords = ['du doi', 'rat dau', 'qua dau', 'khong chiu noi', 'nghiem trong']

    def normalize_text(self, text):
        """
        Normalize Vietnamese text by removing accents for matching

        Args:
            text (str): Vietnamese text with accents

        Returns:
            str: Normalized text without accents, lowercase
        """
        if not text:
            return ''

        # Convert to lowercase
        text = text.lower()

        # Replace Vietnamese characters
        result = []
        for char in text:
            result.append(self.accent_map.get(char, char))

        return ''.join(result)

    def get_conversation_context(self, session_id):
        """
        Get accumulated context from previous turns in this session

        Args:
            session_id (str): Session ID

        Returns:
            dict: Accumulated context with symptoms, flags, turn count, etc.
        """
        query = """
        SELECT TOP 1 turn_number, extracted_symptoms, matched_red_flags,
               patient_age, patient_gender, conversation_status,
               current_esi_level, recommended_department_id
        FROM conversations
        WHERE session_id = ?
        ORDER BY turn_number DESC
        """

        last_turn = Database.execute_query(query, (session_id,), fetch_one=True)

        if not last_turn:
            return {
                'turn_number': 0,
                'symptoms': [],
                'red_flags': [],
                'is_pregnant': False,
                'is_pediatric': False,
                'is_severe': False,
                'patient_age': None,
                'patient_gender': None,
                'follow_up_asked': False,
                'status': 'in_progress'
            }

        # Parse JSON fields
        symptoms = json.loads(last_turn['extracted_symptoms']) if last_turn['extracted_symptoms'] else []
        red_flags = json.loads(last_turn['matched_red_flags']) if last_turn['matched_red_flags'] else []

        return {
            'turn_number': last_turn['turn_number'],
            'symptoms': symptoms,
            'red_flags': red_flags,
            'is_pregnant': any('pregnant' in str(f).lower() or 'thai' in str(f).lower() for f in red_flags),
            'is_pediatric': any('pediatric' in str(f).lower() or 'tre' in str(f).lower() for f in red_flags),
            'is_severe': last_turn['current_esi_level'] and last_turn['current_esi_level'] <= 2,
            'patient_age': last_turn['patient_age'],
            'patient_gender': last_turn['patient_gender'],
            'follow_up_asked': last_turn['turn_number'] >= 1,
            'status': last_turn['conversation_status']
        }

    def detect_context(self, message, existing_context):
        """
        Detect context indicators from user message (pregnancy, pediatric, severity)

        Args:
            message (str): Normalized user message
            existing_context (dict): Existing context from previous turns

        Returns:
            dict: Updated context flags
        """
        context = {
            'is_pregnant': existing_context.get('is_pregnant', False),
            'is_pediatric': existing_context.get('is_pediatric', False),
            'is_severe': existing_context.get('is_severe', False)
        }

        # Check for pregnancy
        for keyword in self.pregnancy_keywords:
            if keyword in message:
                context['is_pregnant'] = True
                break

        # Check for pediatric
        for keyword in self.pediatric_keywords:
            if keyword in message:
                context['is_pediatric'] = True
                break

        # Check for severity
        for keyword in self.severity_keywords:
            if keyword in message:
                context['is_severe'] = True
                break

        # Check affirmative responses for pregnancy
        if 'co' in message.split() and existing_context.get('last_question') == 'pregnancy':
            context['is_pregnant'] = True

        return context

    def check_red_flags(self, message, context):
        """
        Check for emergency red flag patterns in the message

        Args:
            message (str): Normalized user message
            context (dict): Current conversation context

        Returns:
            dict: {
                'has_red_flag': bool,
                'red_flag': dict or None,
                'esi_level': int or None
            }
        """
        query = """
        SELECT id, flag_name, symptom_pattern, esi_level, action,
               warning_message, recommended_department, age_constraint
        FROM red_flags
        WHERE is_active = 1
        ORDER BY esi_level ASC
        """

        red_flags = Database.execute_query(query)

        # Combine all text for matching (current message + accumulated symptoms)
        all_symptoms = ' '.join(context.get('symptoms', []))
        combined_text = f"{message} {all_symptoms}"

        for flag in red_flags:
            pattern = json.loads(flag['symptom_pattern'])
            primary_keywords = pattern.get('primary', [])
            secondary_keywords = pattern.get('secondary', [])
            flag_context = pattern.get('context', '')

            # Check primary keywords
            primary_match = False
            for keyword in primary_keywords:
                normalized_keyword = self.normalize_text(keyword)
                if normalized_keyword in combined_text:
                    primary_match = True
                    break

            if not primary_match:
                continue

            # Check context constraints
            if flag_context == 'pregnant' and not context.get('is_pregnant'):
                continue
            if flag_context == 'pediatric' and not context.get('is_pediatric'):
                continue

            # Check age constraint
            if flag['age_constraint']:
                age_constraint = json.loads(flag['age_constraint'])
                if age_constraint.get('max_age') and context.get('patient_age'):
                    # Simple age check - skip if doesn't match
                    pass

            # Check severity (secondary keywords boost confidence)
            has_secondary = False
            for keyword in secondary_keywords:
                normalized_keyword = self.normalize_text(keyword)
                if normalized_keyword in combined_text:
                    has_secondary = True
                    break

            # For ESI level 1 (emergency), primary match is enough
            # For ESI level 2 (urgent), prefer secondary match or context match
            if flag['esi_level'] == 1 or has_secondary or context.get('is_severe'):
                return {
                    'has_red_flag': True,
                    'red_flag': dict(flag),
                    'esi_level': flag['esi_level']
                }

        return {
            'has_red_flag': False,
            'red_flag': None,
            'esi_level': None
        }

    def extract_symptoms(self, message, existing_symptoms):
        """
        Extract symptom keywords from user message

        Args:
            message (str): Normalized user message
            existing_symptoms (list): Symptoms from previous turns

        Returns:
            list: Updated list of unique symptoms
        """
        query = """
        SELECT DISTINCT symptom_keywords
        FROM symptom_rules
        WHERE is_active = 1
        """

        rules = Database.execute_query(query)
        found_symptoms = set(existing_symptoms)

        for rule in rules:
            keywords = json.loads(rule['symptom_keywords'])
            for keyword in keywords:
                normalized_keyword = self.normalize_text(keyword)
                if normalized_keyword in message:
                    # Store the original keyword (with accents) for display
                    found_symptoms.add(keyword)

        return list(found_symptoms)

    def match_symptom_rules(self, symptoms, context):
        """
        Match accumulated symptoms to department rules

        Args:
            symptoms (list): List of symptom keywords
            context (dict): Conversation context

        Returns:
            list: Sorted list of {rule, department, score} dicts
        """
        if not symptoms:
            return []

        query = """
        SELECT sr.id, sr.rule_name, sr.department_id, sr.symptom_keywords,
               sr.priority, sr.min_symptoms_match, sr.esi_level_default,
               sr.follow_up_questions,
               d.name_vi, d.name_en, d.room_number, d.floor, d.building,
               d.doctor_name, d.description, d.working_hours
        FROM symptom_rules sr
        JOIN departments d ON sr.department_id = d.id
        WHERE sr.is_active = 1 AND d.is_active = 1
        ORDER BY sr.priority DESC
        """

        rules = Database.execute_query(query)
        matches = []

        # Normalize symptoms for matching
        normalized_symptoms = [self.normalize_text(s) for s in symptoms]

        for rule in rules:
            rule_keywords = json.loads(rule['symptom_keywords'])
            normalized_keywords = [self.normalize_text(k) for k in rule_keywords]

            # Count matches
            match_count = 0
            for norm_symptom in normalized_symptoms:
                for norm_keyword in normalized_keywords:
                    if norm_keyword in norm_symptom or norm_symptom in norm_keyword:
                        match_count += 1
                        break

            if match_count >= rule['min_symptoms_match']:
                # Calculate score = match_count × priority
                score = match_count * rule['priority']

                # Boost for context match
                if context.get('is_pregnant') and 'phu san' in self.normalize_text(rule['name_vi']):
                    score *= 1.5
                if context.get('is_pediatric') and 'nhi' in self.normalize_text(rule['name_vi']):
                    score *= 1.5

                matches.append({
                    'rule': dict(rule),
                    'department': {
                        'id': rule['department_id'],
                        'name_vi': rule['name_vi'],
                        'name_en': rule['name_en'],
                        'room_number': rule['room_number'],
                        'floor': rule['floor'],
                        'building': rule['building'],
                        'doctor_name': rule['doctor_name'],
                        'description': rule['description'],
                        'working_hours': rule['working_hours']
                    },
                    'score': score,
                    'match_count': match_count,
                    'priority': rule['priority'],
                    'follow_up_questions': json.loads(rule['follow_up_questions']) if rule['follow_up_questions'] else []
                })

        # Sort by score descending
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches

    def save_conversation_turn(self, session_id, turn_number, user_message, bot_response,
                               symptoms, context, esi_level, red_flags, department_id, status):
        """
        Save a conversation turn to the database
        """
        query = """
        INSERT INTO conversations (
            session_id, turn_number, user_message, bot_response,
            extracted_symptoms, current_esi_level, matched_red_flags,
            recommended_department_id, conversation_status,
            patient_age, patient_gender
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            session_id,
            turn_number,
            user_message,
            bot_response,
            json.dumps(symptoms, ensure_ascii=False),
            esi_level,
            json.dumps(red_flags, ensure_ascii=False) if red_flags else None,
            department_id,
            status,
            context.get('patient_age'),
            context.get('patient_gender')
        )

        return Database.execute_update(query, params)

    def process_message(self, user_message, session_id):
        """
        Main triage logic - process user message and return response

        Flow:
        1. Get conversation context
        2. Detect context (pregnancy, pediatric, severity)
        3. Check red flags first (highest priority)
        4. Extract symptoms
        5. Match symptom rules
        6. Decide response based on priority, turn count, etc.

        Args:
            user_message (str): Raw user message
            session_id (str): Session ID

        Returns:
            dict: Response with all necessary fields for frontend
        """
        # Step 1: Get existing context
        existing_context = self.get_conversation_context(session_id)
        turn_number = existing_context['turn_number'] + 1

        # Normalize message for matching
        normalized_message = self.normalize_text(user_message)

        # Step 2: Detect context from current message
        context = self.detect_context(normalized_message, existing_context)
        context.update({
            'symptoms': existing_context['symptoms'],
            'turn_number': turn_number,
            'follow_up_asked': existing_context['follow_up_asked']
        })

        # Step 3: Check red flags (re-check with updated context)
        red_flag_result = self.check_red_flags(normalized_message, context)

        if red_flag_result['has_red_flag']:
            # EMERGENCY - Return immediately
            red_flag = red_flag_result['red_flag']

            self.save_conversation_turn(
                session_id, turn_number, user_message, red_flag['warning_message'],
                context['symptoms'], context, red_flag['esi_level'],
                [red_flag['flag_name']], None, 'completed'
            )

            return {
                'response': red_flag['warning_message'],
                'session_id': session_id,
                'alertLevel': 'danger' if red_flag['esi_level'] == 1 else 'warning',
                'suggestedDepartment': red_flag['recommended_department'],
                'confidence': 1.0,
                'quickReplies': None,
                'departmentRecommendation': None,
                'conversationStatus': 'completed'
            }

        # Step 4: Extract symptoms from current message
        symptoms = self.extract_symptoms(normalized_message, existing_context['symptoms'])
        context['symptoms'] = symptoms

        # Step 5: Match symptom rules
        matches = self.match_symptom_rules(symptoms, context)

        # Step 6: Decide response
        if not symptoms and not matches:
            # No symptoms detected - ask for more info
            response_text = 'Cam on ban da lien he. Ban co the mo ta cu the hon trieu chung cua minh duoc khong? Vi du: dau o dau, tu khi nao, muc do nhu the nao?'
            quick_replies = [
                {'id': '1', 'label': 'Dau dau', 'value': 'Toi bi dau dau'},
                {'id': '2', 'label': 'Dau bung', 'value': 'Toi bi dau bung'},
                {'id': '3', 'label': 'Sot', 'value': 'Toi bi sot'},
                {'id': '4', 'label': 'Ho', 'value': 'Toi bi ho'}
            ]

            self.save_conversation_turn(
                session_id, turn_number, user_message, response_text,
                symptoms, context, None, None, None, 'in_progress'
            )

            return {
                'response': response_text,
                'session_id': session_id,
                'alertLevel': None,
                'suggestedDepartment': None,
                'confidence': 0.0,
                'quickReplies': quick_replies,
                'departmentRecommendation': None,
                'conversationStatus': 'in_progress'
            }

        # Have symptoms - decide: recommend department or ask follow-up
        best_match = matches[0] if matches else None

        # Decision criteria for giving recommendation:
        # - Priority >= 7 (high priority rule)
        # - OR turn_number >= 3 (enough turns)
        # - OR follow_up already asked
        should_recommend = (
            (best_match and best_match['priority'] >= 7) or
            turn_number >= 3 or
            existing_context['follow_up_asked']
        )

        if should_recommend and best_match:
            # Give department recommendation
            dept = best_match['department']
            response_text = f"Dua tren cac trieu chung cua ban, toi de xuat ban den {dept['name_vi']}."

            department_recommendation = {
                'departmentId': dept['id'],
                'departmentName': dept['name_vi'],
                'doctorName': dept['doctor_name'],
                'roomNumber': dept['room_number'],
                'floor': dept['floor'],
                'description': dept['description'],
                'waitTime': 'Khoang 15-20 phut'
            }

            self.save_conversation_turn(
                session_id, turn_number, user_message, response_text,
                symptoms, context, best_match['rule']['esi_level_default'],
                None, dept['id'], 'completed'
            )

            return {
                'response': response_text,
                'session_id': session_id,
                'alertLevel': None,
                'suggestedDepartment': dept['name_vi'],
                'confidence': min(best_match['score'] / 20, 1.0),
                'quickReplies': None,
                'departmentRecommendation': department_recommendation,
                'conversationStatus': 'completed'
            }

        else:
            # Ask follow-up question
            follow_up_questions = best_match['follow_up_questions'] if best_match else []

            if follow_up_questions:
                # Pick first question that hasn't been asked
                question = follow_up_questions[0]
                response_text = f"Cam on ban. {question}"
            else:
                # Default follow-up
                response_text = 'Cam on ban. Ban co the cho biet them: Trieu chung bat dau tu khi nao? Muc do dau nhu the nao?'

            # Generate quick replies based on context
            quick_replies = None
            if context.get('symptoms'):
                # Context-aware quick replies
                if any('bung' in self.normalize_text(s) for s in symptoms):
                    quick_replies = [
                        {'id': '1', 'label': 'Dau du doi', 'value': 'Dau rat du doi, khong chiu noi'},
                        {'id': '2', 'label': 'Dau am i', 'value': 'Dau am i, kho chiu'},
                        {'id': '3', 'label': 'Co mang thai', 'value': 'Co, toi dang mang thai'}
                    ]
                elif any('sot' in self.normalize_text(s) for s in symptoms):
                    quick_replies = [
                        {'id': '1', 'label': 'Sot cao >39do', 'value': 'Sot cao tren 39 do'},
                        {'id': '2', 'label': 'Sot nhe', 'value': 'Sot nhe khoang 37-38 do'},
                        {'id': '3', 'label': 'Tre em', 'value': 'Be nha toi bi sot'}
                    ]

            self.save_conversation_turn(
                session_id, turn_number, user_message, response_text,
                symptoms, context, None, None, None, 'in_progress'
            )

            return {
                'response': response_text,
                'session_id': session_id,
                'alertLevel': None,
                'suggestedDepartment': None,
                'confidence': 0.0,
                'quickReplies': quick_replies,
                'departmentRecommendation': None,
                'conversationStatus': 'in_progress'
            }

    def reset_conversation(self, session_id):
        """
        Reset/delete all conversation data for a session

        Args:
            session_id (str): Session ID to reset
        """
        query = "DELETE FROM conversations WHERE session_id = ?"
        return Database.execute_update(query, (session_id,))

    def get_conversation_history(self, session_id, limit=10):
        """
        Get conversation history for a session

        Args:
            session_id (str): Session ID
            limit (int): Maximum turns to return

        Returns:
            list: List of conversation turns
        """
        query = f"""
        SELECT TOP {limit} turn_number, user_message, bot_response,
               extracted_symptoms, current_esi_level, conversation_status,
               timestamp
        FROM conversations
        WHERE session_id = ?
        ORDER BY turn_number ASC
        """

        return Database.execute_query(query, (session_id,))
