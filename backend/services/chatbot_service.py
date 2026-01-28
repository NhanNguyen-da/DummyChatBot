"""
chatbot_service.py - Simple Triage Chatbot Logic
Following the spec: 5 turns max, red flags first, score threshold = 7
"""

import json
import re
from models.database import Database


class ChatbotService:
    """
    Simple triage chatbot service
    """

    def __init__(self):
        """Initialize with Vietnamese keyword mappings"""
        # Vietnamese text normalization
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

        # Keywords for context detection
        self.pregnant_keywords = ['mang thai', 'co thai', 'bau', 'thai nghen']
        self.severity_keywords = ['du doi', 'rat dau', 'qua dau', 'khong chiu noi', 'nang', 'rat nang']

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def normalize_text(self, text):
        """Remove Vietnamese accents for matching"""
        if not text:
            return ''
        text = text.lower()
        return ''.join(self.accent_map.get(c, c) for c in text)

    def get_last_turn(self, session_id):
        """Get the last conversation turn for this session"""
        query = """
        SELECT TOP 1 turn_number, extracted_symptoms, patient_age, patient_gender,
               collected_duration, collected_severity, is_pregnant, is_pediatric,
               is_severe, current_score, conversation_status, last_question_type
        FROM conversations
        WHERE session_id = ?
        ORDER BY turn_number DESC
        """
        return Database.execute_query(query, (session_id,), fetch_one=True)

    def extract_age(self, message):
        """Extract age from message"""
        # Pattern: "X tuoi"
        match = re.search(r'(\d+)\s*(tuoi|tuổi)', message)
        if match:
            return int(match.group(1))
        return None

    def extract_gender(self, message):
        """Extract gender from message"""
        if re.search(r'\b(nu|nữ|nu gioi)\b', message):
            return 'nu'
        if re.search(r'\b(nam|nam gioi)\b', message) and 'viet nam' not in message:
            return 'nam'
        return None

    def extract_duration(self, message):
        """Extract duration from message"""
        if re.search(r'\b(hom nay|moi)\b', message):
            return 'hom nay'

        day_match = re.search(r'(\d+)\s*(ngay|ngày)', message)
        if day_match:
            return f"{day_match.group(1)} ngay"

        week_match = re.search(r'(\d+)\s*(tuan|tuần)', message)
        if week_match:
            return f"{week_match.group(1)} tuan"

        return None

    def extract_severity(self, message):
        """Extract severity level (1-10) from message"""
        # Direct number
        match = re.search(r'\b(\d+)\s*/?\s*10\b', message)
        if match:
            return min(int(match.group(1)), 10)

        match = re.search(r'\b(muc|mức)?\s*(\d+)\b', message)
        if match and 1 <= int(match.group(2)) <= 10:
            return int(match.group(2))

        # Keywords
        if any(kw in message for kw in ['rat nang', 'du doi', 'qua dau', 'khong chiu noi']):
            return 8
        if any(kw in message for kw in ['nang', 'nhieu']):
            return 6
        if any(kw in message for kw in ['trung binh', 'vua']):
            return 5
        if any(kw in message for kw in ['nhe', 'it']):
            return 3

        return None

    def check_pregnant(self, message, gender):
        """Check if patient is pregnant"""
        if gender == 'nu' or gender is None:
            for kw in self.pregnant_keywords:
                if kw in message:
                    return True
        return False

    # =========================================================================
    # DATABASE QUERY METHODS
    # =========================================================================

    def check_red_flags(self, message, all_symptoms):
        """
        STEP 1: Check red_flags table for emergency situations
        Returns red_flag info if matched, None otherwise
        """
        query = """
        SELECT id, flag_name, symptom_pattern, esi_level, warning_message,
               recommended_department
        FROM red_flags
        WHERE is_active = 1
        ORDER BY esi_level ASC
        """
        red_flags = Database.execute_query(query)

        # Combine current message with all accumulated symptoms
        combined_text = message + ' ' + ' '.join(all_symptoms)

        for flag in red_flags:
            pattern = json.loads(flag['symptom_pattern'])
            primary_keywords = pattern.get('primary', [])
            secondary_keywords = pattern.get('secondary', [])

            # Check primary keywords
            primary_match = False
            for kw in primary_keywords:
                if self.normalize_text(kw) in combined_text:
                    primary_match = True
                    break

            if not primary_match:
                continue

            # ESI 1: Primary match is enough
            if flag['esi_level'] == 1:
                return flag

            # ESI 2: Need secondary match too
            if flag['esi_level'] == 2:
                for kw in secondary_keywords:
                    if self.normalize_text(kw) in combined_text:
                        return flag

        return None

    def extract_symptoms_from_rules(self, message):
        """
        Extract symptoms by matching against symptom_rules keywords
        """
        query = """
        SELECT DISTINCT symptom_keywords
        FROM symptom_rules
        WHERE is_active = 1
        """
        rules = Database.execute_query(query)

        if not rules:
            print(f"[DEBUG] No symptom rules found in database!")
            return []

        found_symptoms = []
        for rule in rules:
            keywords = json.loads(rule['symptom_keywords'])
            for kw in keywords:
                norm_kw = self.normalize_text(kw)
                if norm_kw in message and kw not in found_symptoms:
                    found_symptoms.append(kw)
                    print(f"[DEBUG] Matched keyword '{kw}' in message")

        return found_symptoms

    def calculate_department_scores(self, all_symptoms, context):
        """
        STEP 2: Calculate scores for each department
        Score = number of UNIQUE keyword matches × 2
        Sum scores by department_id

        IMPORTANT: Filter departments based on patient context:
        - Pediatrics (Khoa Nhi): Only for age < 15
        - OB/GYN (Khoa San Phu Khoa): Only for female patients
        - ENT (Khoa Tai Mui Hong): For all patients
        """
        if not all_symptoms:
            return {}

        query = """
        SELECT sr.department_id, sr.symptom_keywords, d.name_vi, d.name_en
        FROM symptom_rules sr
        JOIN departments d ON sr.department_id = d.id
        WHERE sr.is_active = 1 AND d.is_active = 1
        """
        rules = Database.execute_query(query)

        if not rules:
            return {}

        # Get patient context
        is_pediatric = context.get('is_pediatric', False)
        patient_age = context.get('age')
        patient_gender = context.get('gender')
        is_pregnant = context.get('is_pregnant', False)

        # Normalize symptoms for matching
        norm_symptoms = [self.normalize_text(s) for s in all_symptoms]

        # Track which keywords have been matched for each department (avoid double counting)
        dept_matched_keywords = {}
        dept_names = {}

        for rule in rules:
            dept_id = rule['department_id']
            dept_name = rule['name_vi']
            dept_name_en = rule.get('name_en', '')
            keywords = json.loads(rule['symptom_keywords'])

            # =========================================================
            # FILTER DEPARTMENTS BASED ON PATIENT CONTEXT
            # =========================================================

            # Pediatrics (Khoa Nhi) - Only for children (age < 15)
            if 'Nhi' in dept_name or 'Pediatric' in dept_name_en:
                if patient_age is not None and patient_age >= 15:
                    print(f"[DEBUG] Skipping Pediatrics for adult patient (age={patient_age})")
                    continue  # Skip this rule for adult patients

            # OB/GYN (Khoa San Phu Khoa) - Only for female patients
            if 'San' in dept_name or 'Phu Khoa' in dept_name or 'Obstetric' in dept_name_en or 'Gynecology' in dept_name_en:
                if patient_gender == 'nam':  # Male
                    print(f"[DEBUG] Skipping OB/GYN for male patient")
                    continue  # Skip this rule for male patients

            # =========================================================

            dept_names[dept_id] = dept_name

            if dept_id not in dept_matched_keywords:
                dept_matched_keywords[dept_id] = set()

            # Check each keyword in this rule
            for kw in keywords:
                norm_kw = self.normalize_text(kw)
                # Check if this keyword matches any symptom
                for norm_sym in norm_symptoms:
                    # Exact match OR keyword contains symptom OR symptom contains keyword
                    if norm_kw == norm_sym or norm_kw in norm_sym or norm_sym in norm_kw:
                        dept_matched_keywords[dept_id].add(kw)
                        break

        # Calculate final scores
        dept_scores = {}
        for dept_id, matched_kws in dept_matched_keywords.items():
            match_count = len(matched_kws)
            if match_count > 0:  # Only include departments with matches
                dept_scores[dept_id] = {
                    'department_id': dept_id,
                    'name_vi': dept_names[dept_id],
                    'score': match_count * 2,
                    'match_count': match_count,
                    'matched_keywords': list(matched_kws)
                }

        return dept_scores

    def get_department_info(self, department_id):
        """Query full department information"""
        query = """
        SELECT id, name_vi, name_en, room_number, floor, building,
               doctor_name, description, working_hours
        FROM departments
        WHERE id = ? AND is_active = 1
        """
        return Database.execute_query(query, (department_id,), fetch_one=True)

    def get_quick_replies(self, trigger_type, trigger_value):
        """Query quick replies from database"""
        query = """
        SELECT replies_json
        FROM quick_reply_rules
        WHERE trigger_type = ? AND trigger_value = ? AND is_active = 1
        ORDER BY priority DESC
        """
        result = Database.execute_query(query, (trigger_type, trigger_value), fetch_one=True)

        if result and result.get('replies_json'):
            try:
                return json.loads(result['replies_json'])
            except:
                pass
        return []

    def get_follow_up_question(self, department_id):
        """Get follow-up questions from symptom_rules"""
        query = """
        SELECT follow_up_questions
        FROM symptom_rules
        WHERE department_id = ? AND is_active = 1 AND follow_up_questions IS NOT NULL
        """
        result = Database.execute_query(query, (department_id,), fetch_one=True)

        if result and result.get('follow_up_questions'):
            try:
                questions = json.loads(result['follow_up_questions'])
                if questions:
                    return questions[0]  # Return first question
            except:
                pass
        return None

    # =========================================================================
    # ESI CLASSIFICATION
    # =========================================================================

    def classify_esi_level(self, severity, is_pediatric, is_pregnant, duration):
        """
        Classify ESI level 3, 4, or 5 (1-2 handled by red_flags)
        """
        severity = severity or 0

        # ESI 3: Need exam soon
        if severity >= 5 and severity < 8:
            return 3
        if is_pediatric and severity >= 4:
            return 3
        if is_pregnant and severity >= 4:
            return 3
        if duration and ('tuan' in str(duration) or 'thang' in str(duration)):
            return 3

        # ESI 4: Routine
        if severity >= 3 and severity < 5:
            return 4

        # ESI 5: Low priority
        return 5

    # =========================================================================
    # RESPONSE GENERATION
    # =========================================================================

    def generate_recommendation_response(self, department, esi_level):
        """Generate recommendation response with department info from database"""

        # Base response
        response = f"Dua tren trieu chung cua ban, toi khuyen nghi ban den:\n\n"
        response += f"🏥 {department['name_vi']}\n"
        response += f"📍 Phong {department['room_number']}, Tang {department['floor']}, Toa {department['building']}\n"
        response += f"👨‍⚕️ Bac si: {department['doctor_name']}\n"
        response += f"⏰ Gio lam viec: {department['working_hours']}\n\n"

        # Urgency message based on ESI
        if esi_level == 3:
            response += "📌 Ban nen kham trong vong 1-2 gio toi."
        elif esi_level == 4:
            response += "✅ Trieu chung cua ban co the kham theo lich hen truoc."
        else:
            response += "ℹ️ Trieu chung nhe, ban co the dat lich kham thuong qui."

        return response

    # =========================================================================
    # CONVERSATION SAVE
    # =========================================================================

    def save_turn(self, session_id, turn_number, user_message, bot_response,
                  symptoms, context, esi_level, department_id, status, score):
        """Save one conversation turn as new row"""
        query = """
        INSERT INTO conversations (
            session_id, turn_number, user_message, bot_response,
            extracted_symptoms, patient_age, patient_gender,
            collected_duration, collected_severity,
            is_pregnant, is_pediatric, is_severe,
            current_esi_level, recommended_department_id,
            conversation_status, current_score, last_question_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            session_id,
            turn_number,
            user_message,
            bot_response,
            json.dumps(symptoms, ensure_ascii=False) if symptoms else None,
            context.get('age'),
            context.get('gender'),
            context.get('duration'),
            context.get('severity'),
            context.get('is_pregnant', False),
            context.get('is_pediatric', False),
            context.get('is_severe', False),
            esi_level,
            department_id,
            status,
            score,
            context.get('last_question_type')
        )

        return Database.execute_update(query, params)

    # =========================================================================
    # MAIN PROCESSING LOGIC
    # =========================================================================

    def process_message(self, user_message, session_id):
        """
        Main triage logic - 5 turns max, red flags first, threshold = 7

        Flow (5 turns):
        Turn 1: Symptoms
        Turn 2: Age
        Turn 3: Gender
        Turn 4: Pregnancy (if female > 15) OR Duration (if male or female <= 15)
        Turn 5: Severity
        """
        # Normalize message
        norm_message = self.normalize_text(user_message)

        # Get last turn context
        last_turn = self.get_last_turn(session_id)

        if last_turn:
            turn_number = last_turn['turn_number'] + 1
            prev_symptoms = json.loads(last_turn['extracted_symptoms']) if last_turn['extracted_symptoms'] else []
            # Check if pregnancy was already asked (last_question_type was 'pregnancy' in ANY previous turn)
            last_q_type = last_turn.get('last_question_type')
            context = {
                'age': last_turn['patient_age'],
                'gender': last_turn['patient_gender'],
                'duration': last_turn['collected_duration'],
                'severity': last_turn['collected_severity'],
                'is_pregnant': last_turn['is_pregnant'] or False,
                'is_pediatric': last_turn['is_pediatric'] or False,
                'is_severe': last_turn['is_severe'] or False,
                'last_question_type': last_q_type
            }
        else:
            turn_number = 1
            prev_symptoms = []
            context = {
                'age': None, 'gender': None, 'duration': None, 'severity': None,
                'is_pregnant': False, 'is_pediatric': False, 'is_severe': False,
                'last_question_type': None
            }

        # Extract new information from current message
        new_age = self.extract_age(norm_message)
        new_gender = self.extract_gender(norm_message)
        new_duration = self.extract_duration(norm_message)
        new_severity = self.extract_severity(norm_message)

        # Update context (keep existing if new is None)
        if new_age:
            context['age'] = new_age
            context['is_pediatric'] = new_age < 15
        if new_gender:
            context['gender'] = new_gender
        if new_duration:
            context['duration'] = new_duration
        if new_severity:
            context['severity'] = new_severity
            context['is_severe'] = new_severity >= 7

        # Check pregnancy from keywords in message
        if self.check_pregnant(norm_message, context['gender']):
            context['is_pregnant'] = True

        # If last question was pregnancy and user answered, mark pregnancy as asked
        if context['last_question_type'] == 'pregnancy':
            # User just answered pregnancy question - pregnancy status is now confirmed
            # (either True from keywords or False if no keywords found)
            pass  # is_pregnant is already set above

        # Extract symptoms from current message
        new_symptoms = self.extract_symptoms_from_rules(norm_message)
        all_symptoms = list(set(prev_symptoms + new_symptoms))

        # =====================================================================
        # STEP 1: CHECK RED FLAGS (Highest Priority)
        # =====================================================================
        red_flag = self.check_red_flags(norm_message, all_symptoms)

        if red_flag:
            response = red_flag['warning_message']

            self.save_turn(
                session_id, turn_number, user_message, response,
                all_symptoms, context, red_flag['esi_level'],
                None, 'completed', 10
            )

            return {
                'response': response,
                'session_id': session_id,
                'alertLevel': 'danger' if red_flag['esi_level'] == 1 else 'warning',
                'suggestedDepartment': red_flag['recommended_department'],
                'confidence': 1.0,
                'quickReplies': None,
                'departmentRecommendation': None,
                'conversationStatus': 'completed'
            }

        # =====================================================================
        # STEP 2: CALCULATE SCORES (with patient context filtering)
        # =====================================================================
        dept_scores = self.calculate_department_scores(all_symptoms, context)

        # Debug: Print scoring info
        print(f"[DEBUG] Turn {turn_number}")
        print(f"[DEBUG] Patient context: age={context.get('age')}, gender={context.get('gender')}, is_pediatric={context.get('is_pediatric')}, is_pregnant={context.get('is_pregnant')}")
        print(f"[DEBUG] Extracted symptoms: {all_symptoms}")
        print(f"[DEBUG] Department scores: {dept_scores}")

        # Find best department (highest score)
        best_dept = None
        best_score = 0
        for dept_id, info in dept_scores.items():
            if info['score'] > best_score:
                best_score = info['score']
                best_dept = info

        print(f"[DEBUG] Best dept: {best_dept}, Best score: {best_score}")

        # =====================================================================
        # STEP 3: CHECK REQUIRED INFO AND TURN LIMIT
        # =====================================================================
        THRESHOLD = 7
        MAX_TURNS = 5  # 5 turns for everyone

        # Determine if we need to ask pregnancy
        # Only ask pregnancy if: female AND age > 15 (not pediatric)
        should_ask_pregnancy = (
            context['gender'] == 'nu' and
            context['age'] is not None and
            context['age'] > 15 and
            not context['is_pediatric']
        )

        # Check if pregnancy was already asked (last question was pregnancy)
        pregnancy_already_asked = context['last_question_type'] == 'pregnancy'

        # For female > 15: we ask pregnancy in Turn 4, then severity in Turn 5 (skip duration)
        # For others: we ask duration in Turn 4, then severity in Turn 5

        # Check if all required info is collected based on patient type
        if should_ask_pregnancy:
            # Female > 15: need symptoms, age, gender, pregnancy_asked, severity
            has_all_required_info = (
                all_symptoms and
                context['age'] is not None and
                context['gender'] is not None and
                pregnancy_already_asked and  # Must have asked pregnancy
                context['severity'] is not None
            )
        else:
            # Male or Female <= 15: need symptoms, age, gender, duration, severity
            has_all_required_info = (
                all_symptoms and
                context['age'] is not None and
                context['gender'] is not None and
                context['duration'] is not None and
                context['severity'] is not None
            )

        # =====================================================================
        # CASE 1: Missing required info AND turn < 5 - Ask for missing info
        # =====================================================================
        if not has_all_required_info and turn_number < MAX_TURNS:
            # Determine what to ask next based on turn number
            if not all_symptoms:
                # Turn 1: Ask symptoms
                response = "Xin chao! Ban co the mo ta trieu chung cua minh duoc khong?"
                quick_replies = self.get_quick_replies('default', 'initial')
                context['last_question_type'] = 'symptoms'
            elif context['age'] is None:
                # Turn 2: Ask age
                response = "Ban bao nhieu tuoi?"
                quick_replies = self.get_quick_replies('missing_info', 'age')
                context['last_question_type'] = 'age'
            elif context['gender'] is None:
                # Turn 3: Ask gender
                response = "Gioi tinh cua ban la gi?"
                quick_replies = self.get_quick_replies('missing_info', 'gender')
                context['last_question_type'] = 'gender'
            elif should_ask_pregnancy and not pregnancy_already_asked:
                # Turn 4 (female > 15): Ask pregnancy
                response = "Ban co dang mang thai khong?"
                quick_replies = self.get_quick_replies('missing_info', 'pregnancy')
                context['last_question_type'] = 'pregnancy'
            elif not should_ask_pregnancy and context['duration'] is None:
                # Turn 4 (male or female <= 15): Ask duration
                response = "Trieu chung nay bat dau tu bao lau roi?"
                quick_replies = self.get_quick_replies('missing_info', 'duration')
                context['last_question_type'] = 'duration'
            elif context['severity'] is None:
                # Turn 5: Ask severity
                response = "Muc do dau/kho chiu cua ban the nao? (1-10)"
                quick_replies = self.get_quick_replies('missing_info', 'severity')
                context['last_question_type'] = 'severity'
            else:
                # Fallback - ask for more symptoms
                response = "Ban co trieu chung nao khac khong?"
                quick_replies = self.get_quick_replies('default', 'initial')
                context['last_question_type'] = 'follow_up'

            self.save_turn(
                session_id, turn_number, user_message, response,
                all_symptoms, context, None, None, 'in_progress', best_score
            )

            return {
                'response': response,
                'session_id': session_id,
                'alertLevel': None,
                'suggestedDepartment': None,
                'confidence': min(best_score / 10, 1.0) if best_score else 0.0,
                'quickReplies': quick_replies if quick_replies else None,
                'departmentRecommendation': None,
                'conversationStatus': 'in_progress'
            }

        # =====================================================================
        # CASE 2: All required info collected AND score >= 7 - Recommend
        # =====================================================================
        if has_all_required_info and best_score >= THRESHOLD and best_dept:
            dept_info = self.get_department_info(best_dept['department_id'])
            esi_level = self.classify_esi_level(
                context['severity'], context['is_pediatric'],
                context['is_pregnant'], context['duration']
            )

            response = self.generate_recommendation_response(dept_info, esi_level)

            self.save_turn(
                session_id, turn_number, user_message, response,
                all_symptoms, context, esi_level,
                best_dept['department_id'], 'completed', best_score
            )

            return {
                'response': response,
                'session_id': session_id,
                'alertLevel': None,
                'suggestedDepartment': dept_info['name_vi'],
                'confidence': min(best_score / 10, 1.0),
                'quickReplies': None,
                'departmentRecommendation': {
                    'departmentId': dept_info['id'],
                    'departmentName': dept_info['name_vi'],
                    'roomNumber': dept_info['room_number'],
                    'floor': dept_info['floor'],
                    'building': dept_info['building'],
                    'doctorName': dept_info['doctor_name'],
                    'workingHours': dept_info['working_hours']
                },
                'conversationStatus': 'completed'
            }

        # =====================================================================
        # CASE 3: All info collected but score < 7 AND turn < 5 - Ask follow-up
        # =====================================================================
        if has_all_required_info and best_score < THRESHOLD and turn_number < MAX_TURNS:
            if best_dept:
                follow_up = self.get_follow_up_question(best_dept['department_id'])
                if follow_up:
                    response = follow_up
                else:
                    response = "Ban co trieu chung nao khac khong?"
            else:
                response = "Ban co the mo ta them trieu chung cua minh duoc khong?"
            quick_replies = self.get_quick_replies('default', 'initial')
            context['last_question_type'] = 'follow_up'

            self.save_turn(
                session_id, turn_number, user_message, response,
                all_symptoms, context, None, None, 'in_progress', best_score
            )

            return {
                'response': response,
                'session_id': session_id,
                'alertLevel': None,
                'suggestedDepartment': None,
                'confidence': min(best_score / 10, 1.0) if best_score else 0.0,
                'quickReplies': quick_replies if quick_replies else None,
                'departmentRecommendation': None,
                'conversationStatus': 'in_progress'
            }

        # =====================================================================
        # CASE 4: Turn = 5 (max reached) - Must make final decision
        # =====================================================================
        if best_score > 0 and best_dept:
            # Recommend with available score
            dept_info = self.get_department_info(best_dept['department_id'])
            esi_level = self.classify_esi_level(
                context['severity'], context['is_pediatric'],
                context['is_pregnant'], context['duration']
            )

            response = self.generate_recommendation_response(dept_info, esi_level)

            self.save_turn(
                session_id, turn_number, user_message, response,
                all_symptoms, context, esi_level,
                best_dept['department_id'], 'completed', best_score
            )

            return {
                'response': response,
                'session_id': session_id,
                'alertLevel': None,
                'suggestedDepartment': dept_info['name_vi'],
                'confidence': min(best_score / 10, 1.0),
                'quickReplies': None,
                'departmentRecommendation': {
                    'departmentId': dept_info['id'],
                    'departmentName': dept_info['name_vi'],
                    'roomNumber': dept_info['room_number'],
                    'floor': dept_info['floor'],
                    'building': dept_info['building'],
                    'doctorName': dept_info['doctor_name'],
                    'workingHours': dept_info['working_hours']
                },
                'conversationStatus': 'completed'
            }
        else:
            # Score = 0, cannot suggest
            response = "Toi khong the de xuat khoa kham dua tren mo ta cua ban. Chung toi se goi y ta den ho tro ban."

            self.save_turn(
                session_id, turn_number, user_message, response,
                all_symptoms, context, None, None, 'completed', 0
            )

            return {
                'response': response,
                'session_id': session_id,
                'alertLevel': None,
                'suggestedDepartment': None,
                'confidence': 0.0,
                'quickReplies': None,
                'departmentRecommendation': None,
                'conversationStatus': 'completed'
            }

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def reset_conversation(self, session_id):
        """Reset/delete conversation for a session"""
        query = "DELETE FROM conversations WHERE session_id = ?"
        return Database.execute_update(query, (session_id,))

    def get_conversation_history(self, session_id, limit=10):
        """Get conversation history"""
        query = f"""
        SELECT TOP {limit} turn_number, user_message, bot_response,
               extracted_symptoms, current_esi_level, conversation_status,
               timestamp
        FROM conversations
        WHERE session_id = ?
        ORDER BY turn_number ASC
        """
        return Database.execute_query(query, (session_id,))
