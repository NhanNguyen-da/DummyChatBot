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
        # Pregnancy, Pediatric, Severity, Mild, Negation
        self.pregnancy_keywords = ['mang thai', 'có thai', 'thai nghén', 'bầu', 'thai kỳ']
        self.pediatric_keywords = ['con tôi', 'bé', 'cháu', 'trẻ', 'tháng tuổi', 'tuổi']
        self.severity_keywords = ['dữ dội', 'rất đau', 'quá đau', 'không chịu nổi', 'nặng']
        self.mild_keywords = ['nhẹ', 'ít đau', 'chịu được', 'không đau lắm', 'bình thường']
        self.negation_keywords = ['không', 'chưa', 'hết']  # "not", "not yet", "gone"

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
               current_esi_level, recommended_department_id,
               current_score, is_pregnant, is_pediatric, is_severe,
               collected_duration, collected_location, last_question_type
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
                'is_elderly': False,
                'is_severe': False,
                'patient_age': None,
                'patient_gender': None,
                'collected_duration': None,
                'collected_location': None,
                'current_score': 0,
                'follow_up_asked': False,
                'last_question_type': None,
                'status': 'in_progress'
            }

        # Parse JSON fields
        symptoms = json.loads(last_turn['extracted_symptoms']) if last_turn['extracted_symptoms'] else []
        red_flags = json.loads(last_turn['matched_red_flags']) if last_turn['matched_red_flags'] else []

        # Determine is_elderly from patient_age
        patient_age = last_turn['patient_age']
        is_elderly = True if patient_age and patient_age >= 65 else False

        # Determine is_pregnant and is_pediatric from DB fields or red_flags
        is_pregnant = last_turn['is_pregnant'] if last_turn['is_pregnant'] is not None else any('pregnant' in str(f).lower() or 'thai' in str(f).lower() for f in red_flags)
        is_pediatric = last_turn['is_pediatric'] if last_turn['is_pediatric'] is not None else any('pediatric' in str(f).lower() or 'tre' in str(f).lower() for f in red_flags)
        is_severe = last_turn['is_severe'] if last_turn['is_severe'] is not None else (last_turn['current_esi_level'] and last_turn['current_esi_level'] <= 2)

        return {
            'turn_number': last_turn['turn_number'],
            'symptoms': symptoms,
            'red_flags': red_flags,
            'is_pregnant': is_pregnant,
            'is_pediatric': is_pediatric,
            'is_elderly': is_elderly,
            'is_severe': is_severe,
            'patient_age': patient_age,
            'patient_gender': last_turn['patient_gender'],
            'collected_duration': last_turn['collected_duration'],
            'collected_location': last_turn['collected_location'],
            'current_score': last_turn['current_score'] if last_turn['current_score'] else 0,
            'follow_up_asked': last_turn['turn_number'] >= 1,
            'last_question_type': last_turn['last_question_type'],
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

        # Check for mild keywords first (takes priority over severity)
        is_mild = False
        for keyword in self.mild_keywords:
            if keyword in message:
                is_mild = True
                break

        # Check for severity keywords (but handle negation)
        if not is_mild:
            for keyword in self.severity_keywords:
                if keyword in message:
                    # Check if negation word appears before severity keyword
                    keyword_pos = message.find(keyword)
                    has_negation = False
                    for neg in self.negation_keywords:
                        neg_pos = message.find(neg)
                        # Negation is before keyword and within 15 chars
                        if neg_pos != -1 and neg_pos < keyword_pos and (keyword_pos - neg_pos) < 15:
                            has_negation = True
                            break
                    if not has_negation:
                        context['is_severe'] = True
                        break

        # If mild is detected, explicitly set is_severe to False
        if is_mild:
            context['is_severe'] = False

        # Check affirmative responses for pregnancy
        if 'co' in message.split() and existing_context.get('last_question') == 'pregnancy':
            context['is_pregnant'] = True

        return context

    def calculate_score(self, matched_keywords_count, context, patient_info):
        """
        Calculate total score for department recommendation

        FORMULA: SCORE = keyword_score + context_score + info_score

        SCORING BREAKDOWN:
        - A. Keyword Score (0-5): Based on matched symptoms
             1 keyword = 2 points
             2 keywords = 3 points
             3 keywords = 4 points
             4+ keywords = 5 points

        - B. Context Score (0-3): Based on patient context
             is_pregnant = +1
             is_pediatric = +1
             is_elderly = +1
             is_severe = +1
             (capped at 3 max)

        - C. Info Score (0-2): Based on collected information
             has age = +0.5
             has gender = +0.5
             has duration = +0.5
             has location = +0.5

        THRESHOLD: >= 7 to recommend department
        MAX POSSIBLE: 5 + 3 + 2 = 10 points

        Args:
            matched_keywords_count (int): Number of matched symptom keywords
            context (dict): Contains is_pregnant, is_pediatric, is_elderly, is_severe
            patient_info (dict): Contains age, gender, duration, location

        Returns:
            float: Total score (0-10)
        """
        # A: Keyword Score (0-5) - UPDATED WEIGHTS
        if matched_keywords_count >= 4:
            keyword_score = 5
        elif matched_keywords_count == 3:
            keyword_score = 4
        elif matched_keywords_count == 2:
            keyword_score = 3
        elif matched_keywords_count == 1:
            keyword_score = 2  # Changed from 1 to 2
        else:
            keyword_score = 0

        # B: Context Score (0-3, max 3 points total)
        context_score = 0
        if context.get('is_pregnant'):
            context_score += 1
        if context.get('is_pediatric'):
            context_score += 1
        if context.get('is_elderly'):
            context_score += 1
        if context.get('is_severe'):
            context_score += 1
        context_score = min(context_score, 3)  # Cap at 3

        # C: Information Score (0-2)
        info_score = 0.0
        if patient_info.get('age') is not None:
            info_score += 0.5
        if patient_info.get('gender') is not None:
            info_score += 0.5
        if patient_info.get('duration') is not None:
            info_score += 0.5
        if patient_info.get('location') is not None:
            info_score += 0.5
        info_score = min(info_score, 2.0)  # Cap at 2

        total_score = keyword_score + context_score + info_score
        return min(total_score, 10.0)  # Cap at 10

    def extract_age_gender(self, message):
        """
        Extract age and gender from user message

        Args:
            message (str): Normalized message

        Returns:
            dict: {'age': int or None, 'gender': str or None, 'is_pediatric': bool, 'is_elderly': bool}
        """
        result = {
            'age': None,
            'gender': None,
            'is_pediatric': False,
            'is_elderly': False
        }

        # Age patterns (Vietnamese)
        # Pattern: "duoi 15 tuoi" (under 15)
        under_match = re.search(r'duoi\s+(\d+)\s*(tuoi|tuổi)', message)
        if under_match:
            age_limit = int(under_match.group(1))
            result['age'] = age_limit - 1
            if age_limit <= 15:
                result['is_pediatric'] = True

        # Pattern: "tren 65 tuoi" (over 65)
        over_match = re.search(r'tren\s+(\d+)\s*(tuoi|tuổi)', message)
        if over_match:
            age_limit = int(over_match.group(1))
            result['age'] = age_limit + 5
            if age_limit >= 65:
                result['is_elderly'] = True

        # Pattern: "15-40 tuoi" or "15 den 40 tuoi"
        range_match = re.search(r'(\d+)\s*[-–]\s*(\d+)\s*(tuoi|tuổi)', message)
        if not range_match:
            range_match = re.search(r'(\d+)\s+den\s+(\d+)\s*(tuoi|tuổi)?', message)
        if range_match:
            low = int(range_match.group(1))
            high = int(range_match.group(2))
            result['age'] = (low + high) // 2
            if result['age'] < 15:
                result['is_pediatric'] = True
            elif result['age'] >= 65:
                result['is_elderly'] = True

        # Pattern: exact age "X tuoi" or "X tuổi"
        if result['age'] is None:
            exact_match = re.search(r'(\d+)\s*(tuoi|tuổi)', message)
            if exact_match:
                result['age'] = int(exact_match.group(1))
                if result['age'] < 15:
                    result['is_pediatric'] = True
                elif result['age'] >= 65:
                    result['is_elderly'] = True

        # Gender patterns (Vietnamese)
        if re.search(r'\b(la\s+nam|nam\s+gioi)\b', message) or (re.search(r'\bnam\b', message) and not re.search(r'viet\s*nam', message)):
            result['gender'] = 'male'
        elif re.search(r'\b(la\s+nu|nu\s+gioi|nữ)\b', message) or re.search(r'\bnu\b', message):
            result['gender'] = 'female'

        # Pediatric detection (if no age provided)
        if result['age'] is None:
            pediatric_keywords = ['con toi', 'be', 'chau', 'tre em', 'thang tuoi']
            for keyword in pediatric_keywords:
                if keyword in message:
                    result['is_pediatric'] = True
                    break

        # Elderly detection (if no age provided)
        if result['age'] is None:
            elderly_keywords = ['gia', 'cao tuoi', 'lon tuoi']
            for keyword in elderly_keywords:
                if keyword in message:
                    result['is_elderly'] = True
                    break

        return result

    def extract_duration_location(self, message):
        """
        Extract symptom duration and pain location

        Args:
            message (str): Normalized message

        Returns:
            dict: {'duration': str or None, 'location': str or None}
        """
        result = {
            'duration': None,
            'location': None
        }

        # Duration patterns
        # "hom nay", "moi" (today, new)
        if re.search(r'\b(hom nay|moi)\b', message):
            result['duration'] = 'hom nay'

        # "X ngay" (X days)
        day_match = re.search(r'(\d+)\s*(ngay|ngày)', message)
        if day_match:
            result['duration'] = f"{day_match.group(1)} ngay"

        # "X tuan" (X weeks)
        week_match = re.search(r'(\d+)\s*(tuan|tuần)', message)
        if week_match:
            result['duration'] = f"{week_match.group(1)} tuan"

        # "X thang" (X months)
        month_match = re.search(r'(\d+)\s*(thang|tháng)', message)
        if month_match:
            result['duration'] = f"{month_match.group(1)} thang"

        # Location patterns
        location_patterns = [
            (r'bung\s+tren', 'bung tren'),
            (r'bung\s+duoi', 'bung duoi'),
            (r'ben\s+phai', 'ben phai'),
            (r'ben\s+trai', 'ben trai'),
            (r'nguc\s+trai', 'nguc trai'),
            (r'nguc\s+phai', 'nguc phai'),
            (r'nua\s+dau', 'nua dau'),
            (r'\bdau\b', 'dau')
        ]

        for pattern, location_name in location_patterns:
            if re.search(pattern, message):
                result['location'] = location_name
                break

        return result

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

            # Check secondary keywords
            has_secondary = False
            for keyword in secondary_keywords:
                normalized_keyword = self.normalize_text(keyword)
                if normalized_keyword in combined_text:
                    has_secondary = True
                    break

            # Red flag trigger logic:
            # - ESI level 1 (emergency): primary match is enough (chest pain, stroke, etc.)
            # - ESI level 2 (urgent): REQUIRES secondary keyword match
            #   (simple symptoms should go through 5-turn flow, not bypass)
            if flag['esi_level'] == 1:
                # Emergency - trigger on primary match alone
                return {
                    'has_red_flag': True,
                    'red_flag': dict(flag),
                    'esi_level': flag['esi_level']
                }
            elif flag['esi_level'] == 2 and has_secondary:
                # Urgent - only trigger if secondary keywords also match
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

    def get_quick_replies_from_db(self, trigger_type, trigger_value):
        """
        Query quick replies from quick_reply_rules table

        Args:
            trigger_type (str): Type of trigger - 'symptom', 'missing_info', 'context', 'default'
            trigger_value (str): Value to match - e.g., 'dau bung', 'age', 'pregnant'

        Returns:
            list: List of quick reply dicts [{"id": "", "label": "", "value": ""}] or empty list
        """
        query = """
        SELECT replies_json
        FROM quick_reply_rules
        WHERE trigger_type = ?
          AND trigger_value = ?
          AND is_active = 1
        ORDER BY priority DESC
        """

        result = Database.execute_query(query, (trigger_type, trigger_value), fetch_one=True)

        if not result or not result.get('replies_json'):
            return []

        try:
            replies = json.loads(result['replies_json'])
            return replies if isinstance(replies, list) else []
        except (json.JSONDecodeError, TypeError):
            return []

    def determine_missing_info(self, context):
        """
        Determine what patient information is still missing

        Args:
            context (dict): Current conversation context

        Returns:
            list: List of missing info types
        """
        missing = []

        if not context.get('patient_age'):
            missing.append('age')

        if not context.get('patient_gender'):
            missing.append('gender')

        if not context.get('collected_duration'):
            missing.append('duration')

        if not context.get('collected_location'):
            missing.append('location')

        return missing

    def get_dynamic_quick_replies(self, symptoms, context, missing_info):
        """
        Generate dynamic quick replies based on current conversation state

        Priority order:
        1. Missing critical info (age, gender) - highest priority
        2. Context-specific (pregnant, pediatric, elderly)
        3. Symptom-specific
        4. Default replies (if nothing else matches)

        Args:
            symptoms (list): List of extracted symptoms
            context (dict): Contains is_pregnant, is_pediatric, is_elderly, is_severe
            missing_info (list): List of missing info types - ['age', 'gender', 'duration', 'location']

        Returns:
            list: List of quick reply dicts, max 5 items
        """
        replies = []

        # Priority 1: Missing critical info
        if 'age' in missing_info:
            replies.extend(self.get_quick_replies_from_db('missing_info', 'age'))

        if 'gender' in missing_info and len(replies) < 5:
            replies.extend(self.get_quick_replies_from_db('missing_info', 'gender'))

        # Priority 2: Context-specific
        if context.get('is_pregnant') and len(replies) < 5:
            replies.extend(self.get_quick_replies_from_db('context', 'pregnant'))

        if context.get('is_pediatric') and len(replies) < 5:
            replies.extend(self.get_quick_replies_from_db('context', 'pediatric'))

        if context.get('is_elderly') and len(replies) < 5:
            replies.extend(self.get_quick_replies_from_db('context', 'elderly'))

        # Priority 3: Symptom-specific
        if len(replies) < 5:
            for symptom in symptoms:
                normalized_symptom = self.normalize_text(symptom)
                symptom_replies = self.get_quick_replies_from_db('symptom', normalized_symptom)
                replies.extend(symptom_replies)
                if len(replies) >= 5:
                    break

        # Priority 4: Default (if no replies found)
        if not replies:
            replies = self.get_quick_replies_from_db('default', 'initial')

        # Limit to max 5 replies
        return replies[:5]

    def generate_turn_based_question(self, turn_number, context):
        """
        Generate follow-up question based on turn number (structured 5-turn flow)

        FLOW:
        - Turn 1: User gave symptoms → Ask age + gender
        - Turn 2: User gave age/gender →
            - If pregnant: Ask severity → then recommend OB/GYN or Emergency
            - If not pregnant: Ask location
        - Turn 3: User gave location → Ask duration
        - Turn 4: User gave duration → Ask severity
        - Turn 5: Force recommend based on collected info

        PREGNANT PATH (shortcut):
        - After detecting pregnancy, ask severity immediately
        - Severe → Emergency (Cap cuu san khoa)
        - Mild → OB/GYN (Khoa San Phu Khoa)

        Args:
            turn_number (int): Current turn number (just processed)
            context (dict): Conversation context

        Returns:
            tuple: (question_text, question_type)
        """
        # Check for pregnant path - special handling
        if context.get('is_pregnant'):
            # If pregnant and severity not yet collected, ask severity
            if not context.get('is_severe') and context.get('last_question_type') != 'pregnant_severity':
                return (
                    'Ban dang mang thai. Muc do dau/kho chiu cua ban nhu the nao? Nhe hay du doi?',
                    'pregnant_severity'
                )

        # Normal flow based on turn number
        if turn_number == 1:
            # After Turn 1 (symptoms received), ask age + gender
            return (
                'Xin cho biet tuoi va gioi tinh cua ban? (Vi du: 30 tuoi, nu)',
                'age_gender'
            )

        elif turn_number == 2:
            # After Turn 2 (age/gender received), ask location
            return (
                'Ban co the cho biet vi tri dau cu the khong? (Vi du: bung tren, bung duoi, ben phai, ben trai)',
                'location'
            )

        elif turn_number == 3:
            # After Turn 3 (location received), ask duration
            return (
                'Trieu chung nay bat dau tu khi nao? (Vi du: hom nay, 2 ngay, 1 tuan)',
                'duration'
            )

        elif turn_number == 4:
            # After Turn 4 (duration received), ask severity
            return (
                'Muc do dau cua ban nhu the nao? Nhe, trung binh hay du doi?',
                'severity'
            )

        else:
            # Turn 5+ - should trigger recommendation, fallback question
            return (
                'Ban co trieu chung nao khac can bo sung khong?',
                'other'
            )

    def get_pregnant_recommendation(self, context):
        """
        Get department recommendation for pregnant patient based on severity

        Args:
            context (dict): Conversation context with is_severe flag

        Returns:
            dict: Department recommendation with response text
        """
        if context.get('is_severe'):
            # Severe → Emergency
            return {
                'department_name': 'Cap cuu San khoa',
                'response': 'KHAN CAP: Ban dang mang thai va co trieu chung nghiem trong. Vui long den Cap cuu San khoa ngay lap tuc!',
                'esi_level': 2,
                'alert_level': 'warning'
            }
        else:
            # Mild → OB/GYN
            return {
                'department_name': 'Khoa San Phu Khoa',
                'response': 'Dua tren tinh trang cua ban, toi de xuat ban den Khoa San Phu Khoa de duoc kham va tu van.',
                'esi_level': 4,
                'alert_level': None
            }

    def save_conversation_turn(self, session_id, turn_number, user_message, bot_response,
                               symptoms, context, esi_level, red_flags, department_id, status,
                               score=0):
        """
        Save a conversation turn to the database

        Args:
            session_id: Session identifier
            turn_number: Current turn number
            user_message: User's message
            bot_response: Bot's response
            symptoms: List of extracted symptoms
            context: Conversation context dict
            esi_level: ESI level
            red_flags: List of matched red flags
            department_id: Recommended department ID
            status: Conversation status
            score: Current score (0-10)
        """
        query = """
        INSERT INTO conversations (
            session_id, turn_number, user_message, bot_response,
            extracted_symptoms, current_esi_level, matched_red_flags,
            recommended_department_id, conversation_status,
            patient_age, patient_gender,
            current_score, is_pregnant, is_pediatric, is_severe,
            collected_duration, collected_location, last_question_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            context.get('patient_gender'),
            score,
            context.get('is_pregnant', False),
            context.get('is_pediatric', False),
            context.get('is_severe', False),
            context.get('collected_duration'),
            context.get('collected_location'),
            context.get('last_question_type')
        )

        return Database.execute_update(query, params)

    def process_message(self, user_message, session_id):
        """
        Main triage logic - process user message and return response

        STRUCTURED 5-TURN FLOW:
        Turn 1: User describes symptoms → Bot asks age + gender
        Turn 2: User gives age/gender →
                - If pregnant: Bot asks severity → recommend OB/GYN or Emergency
                - If not pregnant: Bot asks location
        Turn 3: User gives location → Bot asks duration
        Turn 4: User gives duration → Bot asks severity
        Turn 5: User gives severity → Bot recommends department

        RED FLAGS: Checked at every turn, bypass flow if detected

        Args:
            user_message (str): Raw user message
            session_id (str): Session ID

        Returns:
            dict: Response with all necessary fields for frontend
        """
        # Step 1: Get existing context
        existing_context = self.get_conversation_context(session_id)
        turn_number = existing_context['turn_number'] + 1

        # Step 2: Normalize message for matching
        normalized_message = self.normalize_text(user_message)

        # Step 3: Extract age/gender from current message
        age_gender_info = self.extract_age_gender(normalized_message)

        # Step 4: Extract duration/location from current message
        duration_location_info = self.extract_duration_location(normalized_message)

        # Step 5: Detect context from current message (pregnancy, severity)
        context = self.detect_context(normalized_message, existing_context)

        # Merge extracted info with existing context (keep existing if not None)
        context['patient_age'] = existing_context.get('patient_age') or age_gender_info.get('age')
        context['patient_gender'] = existing_context.get('patient_gender') or age_gender_info.get('gender')
        context['collected_duration'] = existing_context.get('collected_duration') or duration_location_info.get('duration')
        context['collected_location'] = existing_context.get('collected_location') or duration_location_info.get('location')

        # Update is_pediatric and is_elderly from age extraction
        if age_gender_info.get('is_pediatric'):
            context['is_pediatric'] = True
        if age_gender_info.get('is_elderly'):
            context['is_elderly'] = True
        else:
            context['is_elderly'] = existing_context.get('is_elderly', False)

        context.update({
            'symptoms': existing_context['symptoms'],
            'turn_number': turn_number,
            'follow_up_asked': existing_context['follow_up_asked'],
            'last_question_type': existing_context.get('last_question_type')
        })

        # Step 6: Check red flags at EVERY turn (bypass flow if detected)
        red_flag_result = self.check_red_flags(normalized_message, context)

        if red_flag_result['has_red_flag']:
            # EMERGENCY - Return immediately, bypass turn flow
            red_flag = red_flag_result['red_flag']

            self.save_conversation_turn(
                session_id, turn_number, user_message, red_flag['warning_message'],
                context['symptoms'], context, red_flag['esi_level'],
                [red_flag['flag_name']], None, 'completed',
                score=10  # Max score for emergency
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

        # Step 7: Extract symptoms from current message
        symptoms = self.extract_symptoms(normalized_message, existing_context['symptoms'])
        context['symptoms'] = symptoms

        # Step 8: Match symptom rules
        matches = self.match_symptom_rules(symptoms, context)
        best_match = matches[0] if matches else None

        # Step 9: Calculate score
        score = self.calculate_score(
            matched_keywords_count=len(symptoms),
            context={
                'is_pregnant': context.get('is_pregnant', False),
                'is_pediatric': context.get('is_pediatric', False),
                'is_elderly': context.get('is_elderly', False),
                'is_severe': context.get('is_severe', False)
            },
            patient_info={
                'age': context.get('patient_age'),
                'gender': context.get('patient_gender'),
                'duration': context.get('collected_duration'),
                'location': context.get('collected_location')
            }
        )

        # =====================================================================
        # PREGNANT PATH - Special handling (shortcut to recommendation)
        # =====================================================================
        if context.get('is_pregnant'):
            # Check if we already asked severity for pregnant patient
            if existing_context.get('last_question_type') == 'pregnant_severity':
                # User just answered severity question → Recommend now
                recommendation = self.get_pregnant_recommendation(context)

                # Find OB/GYN department from matches or use default
                dept_id = None
                dept_info = None
                for m in matches:
                    if 'san' in self.normalize_text(m['department']['name_vi']):
                        dept_id = m['department']['id']
                        dept_info = m['department']
                        break

                self.save_conversation_turn(
                    session_id, turn_number, user_message, recommendation['response'],
                    symptoms, context, recommendation['esi_level'],
                    None, dept_id, 'completed',
                    score=score
                )

                department_recommendation = None
                if dept_info:
                    department_recommendation = {
                        'departmentId': dept_info['id'],
                        'departmentName': dept_info['name_vi'],
                        'doctorName': dept_info.get('doctor_name'),
                        'roomNumber': dept_info.get('room_number'),
                        'floor': dept_info.get('floor'),
                        'description': dept_info.get('description'),
                        'waitTime': 'Khoang 15-20 phut'
                    }

                return {
                    'response': recommendation['response'],
                    'session_id': session_id,
                    'alertLevel': recommendation['alert_level'],
                    'suggestedDepartment': recommendation['department_name'],
                    'confidence': 1.0,
                    'quickReplies': None,
                    'departmentRecommendation': department_recommendation,
                    'conversationStatus': 'completed'
                }
            else:
                # Pregnant detected but haven't asked severity yet → Ask severity
                response_text, question_type = self.generate_turn_based_question(turn_number, context)
                context['last_question_type'] = question_type

                # Quick replies for pregnant severity
                quick_replies = self.get_quick_replies_from_db('missing_info', 'severity')

                self.save_conversation_turn(
                    session_id, turn_number, user_message, response_text,
                    symptoms, context, None, None, None, 'in_progress',
                    score=score
                )

                return {
                    'response': response_text,
                    'session_id': session_id,
                    'alertLevel': None,
                    'suggestedDepartment': None,
                    'confidence': min(score / 10, 1.0),
                    'quickReplies': quick_replies if quick_replies else None,
                    'departmentRecommendation': None,
                    'conversationStatus': 'in_progress'
                }

        # =====================================================================
        # NORMAL PATH - 5-turn structured flow
        # =====================================================================

        # No symptoms yet - ask for symptoms first (Turn 0 -> 1)
        if not symptoms and not matches:
            response_text = 'Cam on ban da lien he. Ban co the mo ta cu the trieu chung cua minh duoc khong? Vi du: dau dau, dau bung, sot, ho...'
            quick_replies = self.get_quick_replies_from_db('default', 'initial')
            context['last_question_type'] = 'symptom'

            self.save_conversation_turn(
                session_id, turn_number, user_message, response_text,
                symptoms, context, None, None, None, 'in_progress',
                score=0
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

        # Decision: Recommend or continue asking based on turn number and score
        # Turn 5 or score >= 7 → Force recommendation
        should_recommend = (turn_number >= 5) or (score >= 7)

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
                None, dept['id'], 'completed',
                score=score
            )

            return {
                'response': response_text,
                'session_id': session_id,
                'alertLevel': None,
                'suggestedDepartment': dept['name_vi'],
                'confidence': min(score / 10, 1.0),
                'quickReplies': None,
                'departmentRecommendation': department_recommendation,
                'conversationStatus': 'completed'
            }

        # =====================================================================
        # CONTINUE TURN-BASED FLOW (Turn 1-4)
        # =====================================================================

        # Generate question based on current turn number
        response_text, question_type = self.generate_turn_based_question(turn_number, context)
        context['last_question_type'] = question_type

        # Get appropriate quick replies based on question type
        if question_type == 'age_gender':
            quick_replies = self.get_quick_replies_from_db('missing_info', 'age')
        elif question_type == 'location':
            # Get symptom-specific location quick replies
            quick_replies = []
            for symptom in symptoms:
                normalized_symptom = self.normalize_text(symptom)
                symptom_replies = self.get_quick_replies_from_db('symptom', f'{normalized_symptom}_location')
                if symptom_replies:
                    quick_replies.extend(symptom_replies)
                    break
            if not quick_replies:
                quick_replies = self.get_quick_replies_from_db('symptom', 'dau bung_location')
        elif question_type == 'duration':
            quick_replies = self.get_quick_replies_from_db('missing_info', 'duration')
        elif question_type == 'severity':
            quick_replies = self.get_quick_replies_from_db('missing_info', 'severity')
        else:
            quick_replies = self.get_quick_replies_from_db('default', 'initial')

        self.save_conversation_turn(
            session_id, turn_number, user_message, response_text,
            symptoms, context, None, None, None, 'in_progress',
            score=score
        )

        return {
            'response': response_text,
            'session_id': session_id,
            'alertLevel': None,
            'suggestedDepartment': None,
            'confidence': min(score / 10, 1.0),
            'quickReplies': quick_replies if quick_replies else None,
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
