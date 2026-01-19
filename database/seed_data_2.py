"""
seed_data_2.py - Seed Data cho Demo Chatbot Triage
Chứa 6 chuyên khoa chính: Tai Mũi Họng, Da Liễu, Tim Mạch, Phụ Sản, Nhi Khoa, Tiêu Hóa

Usage:
    python seed_data_2.py
"""

import sqlite3
import sys
import json
from pathlib import Path

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Database path
DB_PATH = Path(__file__).parent / 'chatbot.db'


def seed_departments(cursor):
    """
    Seed 6 chuyên khoa chính cho demo
    """
    departments = [
        {
            'name_vi': 'Tai Mũi Họng',
            'name_en': 'ENT (Ear, Nose, Throat)',
            'room_number': '310',
            'floor': 'Tầng 3',
            'building': 'Khu A',
            'doctor_name': 'BS. Nguyễn Văn An',
            'description': 'Chuyên khám và điều trị các bệnh về tai, mũi, họng, đầu cổ',
            'working_hours': 'Thứ 2-7: 7:00-17:00'
        },
        {
            'name_vi': 'Da Liễu',
            'name_en': 'Dermatology',
            'room_number': '205',
            'floor': 'Tầng 2',
            'building': 'Khu A',
            'doctor_name': 'BS. Trần Thị Bình',
            'description': 'Chuyên khám và điều trị các bệnh về da, mụn, viêm da, nấm da',
            'working_hours': 'Thứ 2-6: 8:00-17:00'
        },
        {
            'name_vi': 'Tim Mạch',
            'name_en': 'Cardiology',
            'room_number': '405',
            'floor': 'Tầng 4',
            'building': 'Khu B',
            'doctor_name': 'BS. Lê Văn Cường',
            'description': 'Chuyên khám và điều trị các bệnh về tim mạch, huyết áp, rối loạn nhịp tim',
            'working_hours': 'Thứ 2-6: 7:00-17:00, Thứ 7: 7:00-12:00'
        },
        {
            'name_vi': 'Phụ Sản',
            'name_en': 'Obstetrics & Gynecology',
            'room_number': '305',
            'floor': 'Tầng 3',
            'building': 'Khu C',
            'doctor_name': 'BS. Phạm Thị Dung',
            'description': 'Chuyên khám và điều trị bệnh phụ khoa, sản khoa, theo dõi thai nghén',
            'working_hours': 'Thứ 2-7: 7:00-17:00'
        },
        {
            'name_vi': 'Nhi Khoa',
            'name_en': 'Pediatrics',
            'room_number': '505',
            'floor': 'Tầng 5',
            'building': 'Khu C',
            'doctor_name': 'BS. Hoàng Văn Em',
            'description': 'Chuyên khám và điều trị bệnh cho trẻ em từ 0-16 tuổi',
            'working_hours': 'Thứ 2-CN: 7:00-20:00'
        },
        {
            'name_vi': 'Tiêu Hóa',
            'name_en': 'Gastroenterology',
            'room_number': '410',
            'floor': 'Tầng 4',
            'building': 'Khu B',
            'doctor_name': 'BS. Võ Thị Phượng',
            'description': 'Chuyên khám và điều trị các bệnh về dạ dày, ruột, gan, mật',
            'working_hours': 'Thứ 2-6: 7:00-17:00'
        }
    ]

    print("Seeding departments table...")
    for dept in departments:
        cursor.execute("""
            INSERT INTO departments (
                name_vi, name_en, room_number, floor, building,
                doctor_name, description, working_hours
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dept['name_vi'], dept['name_en'], dept['room_number'],
            dept['floor'], dept['building'], dept['doctor_name'],
            dept['description'], dept['working_hours']
        ))

    print(f"✅ Added {len(departments)} departments")


def seed_symptom_rules(cursor):
    """
    Seed symptom rules cho 6 chuyên khoa
    """
    # Get department IDs
    cursor.execute("SELECT id, name_vi FROM departments")
    dept_map = {name: id for id, name in cursor.fetchall()}

    symptom_rules = [
        # ==================== TAI MŨI HỌNG ====================
        {
            'rule_name': 'Đau họng + Sốt',
            'department': 'Tai Mũi Họng',
            'symptom_keywords': json.dumps([
                'đau họng', 'đau cổ họng', 'nuốt đau', 'viêm họng',
                'amidan sưng', 'họng đỏ'
            ], ensure_ascii=False),
            'priority': 7,
            'min_symptoms_match': 1,
            'esi_level_default': 3,
            'follow_up_questions': json.dumps([
                'Bạn có bị sốt không?',
                'Có khó nuốt hoặc nuốt rất đau không?',
                'Có sưng hạch ở cổ không?'
            ], ensure_ascii=False),
            'additional_notes': 'Common pharyngitis or tonsillitis'
        },
        {
            'rule_name': 'Nghẹt mũi + Ho',
            'department': 'Tai Mũi Họng',
            'symptom_keywords': json.dumps([
                'nghẹt mũi', 'sổ mũi', 'ho', 'viêm mũi',
                'chảy nước mũi', 'mũi bị tắc'
            ], ensure_ascii=False),
            'priority': 5,
            'min_symptoms_match': 1,
            'esi_level_default': 4,
            'follow_up_questions': json.dumps([
                'Triệu chứng kéo dài bao lâu rồi?',
                'Có đau đầu hoặc đau quanh mắt không?',
                'Nước mũi màu gì - trong suốt hay vàng xanh?'
            ], ensure_ascii=False),
            'additional_notes': 'Possible rhinitis or sinusitis'
        },
        {
            'rule_name': 'Đau tai',
            'department': 'Tai Mũi Họng',
            'symptom_keywords': json.dumps([
                'đau tai', 'tai đau', 'viêm tai', 'chảy mủ tai',
                'ù tai', 'nghe kém'
            ], ensure_ascii=False),
            'priority': 6,
            'min_symptoms_match': 1,
            'esi_level_default': 3,
            'follow_up_questions': json.dumps([
                'Tai nào bị đau?',
                'Có chảy dịch hoặc mủ từ tai không?',
                'Có giảm thính lực không?'
            ], ensure_ascii=False),
            'additional_notes': 'Possible otitis media or externa'
        },

        # ==================== DA LIỄU ====================
        {
            'rule_name': 'Ngứa + Nổi mẩn',
            'department': 'Da Liễu',
            'symptom_keywords': json.dumps([
                'ngứa', 'ngứa da', 'nổi mẩn', 'phát ban',
                'mẩn đỏ', 'da ngứa'
            ], ensure_ascii=False),
            'priority': 5,
            'min_symptoms_match': 1,
            'esi_level_default': 4,
            'follow_up_questions': json.dumps([
                'Vị trí ngứa ở đâu trên cơ thể?',
                'Có tiếp xúc với gì mới không? (thực phẩm, mỹ phẩm, hóa chất)',
                'Da có sưng đỏ hoặc chảy nước không?'
            ], ensure_ascii=False),
            'additional_notes': 'Possible allergic reaction or dermatitis'
        },
        {
            'rule_name': 'Mụn + Viêm da',
            'department': 'Da Liễu',
            'symptom_keywords': json.dumps([
                'mụn', 'mụn trứng cá', 'viêm da', 'da mặt',
                'mụn đỏ', 'mụn mủ'
            ], ensure_ascii=False),
            'priority': 4,
            'min_symptoms_match': 1,
            'esi_level_default': 5,
            'follow_up_questions': json.dumps([
                'Mụn xuất hiện ở đâu? (mặt, lưng, ngực)',
                'Đã kéo dài bao lâu?',
                'Có đau hoặc sưng không?'
            ], ensure_ascii=False),
            'additional_notes': 'Acne vulgaris or folliculitis'
        },
        {
            'rule_name': 'Nấm da',
            'department': 'Da Liễu',
            'symptom_keywords': json.dumps([
                'nấm', 'nấm da', 'lang ben', 'hắc lào',
                'vết tròn ngứa', 'vảy da'
            ], ensure_ascii=False),
            'priority': 4,
            'min_symptoms_match': 1,
            'esi_level_default': 5,
            'follow_up_questions': json.dumps([
                'Vết nấm ở đâu? (chân, tay, da đầu)',
                'Có lan rộng không?',
                'Đã điều trị gì chưa?'
            ], ensure_ascii=False),
            'additional_notes': 'Fungal infection - tinea'
        },

        # ==================== TIM MẠCH ====================
        {
            'rule_name': 'Đau ngực - Cardiac',
            'department': 'Tim Mạch',
            'symptom_keywords': json.dumps([
                'đau ngực', 'đau tim', 'tức ngực', 'thắt ngực',
                'ngực nặng'
            ], ensure_ascii=False),
            'priority': 9,
            'min_symptoms_match': 1,
            'esi_level_default': 2,
            'follow_up_questions': json.dumps([
                '⚠️ Cơn đau có lan ra cánh tay trái, vai, hoặc hàm không?',
                '⚠️ Có đổ mồ hôi, buồn nôn, khó thở không?',
                '⚠️ Đau xuất hiện khi nào? Khi nghỉ hay khi vận động?'
            ], ensure_ascii=False),
            'additional_notes': 'HIGH PRIORITY - Possible ACS (Acute Coronary Syndrome)'
        },
        {
            'rule_name': 'Tim đập nhanh',
            'department': 'Tim Mạch',
            'symptom_keywords': json.dumps([
                'tim đập nhanh', 'hồi hộp', 'tim đập loạn',
                'tim đập mạnh', 'trống ngực'
            ], ensure_ascii=False),
            'priority': 6,
            'min_symptoms_match': 1,
            'esi_level_default': 3,
            'follow_up_questions': json.dumps([
                'Có chóng mặt hoặc sắp ngất không?',
                'Tim đập nhanh có đều đặn không?',
                'Có sau khi uống cà phê hoặc thuốc không?'
            ], ensure_ascii=False),
            'additional_notes': 'Possible arrhythmia - palpitations'
        },
        {
            'rule_name': 'Huyết áp cao',
            'department': 'Tim Mạch',
            'symptom_keywords': json.dumps([
                'huyết áp cao', 'đau đầu dữ dội', 'chảy máu cam',
                'nhìn mờ', 'chóng mặt'
            ], ensure_ascii=False),
            'priority': 7,
            'min_symptoms_match': 2,
            'esi_level_default': 3,
            'follow_up_questions': json.dumps([
                'Huyết áp đo được bao nhiêu?',
                'Có uống thuốc huyết áp không?',
                'Có đau ngực hoặc khó thở kèm theo không?'
            ], ensure_ascii=False),
            'additional_notes': 'Possible hypertensive crisis'
        },

        # ==================== PHỤ SẢN ====================
        {
            'rule_name': 'Đau bụng dưới - Phụ khoa',
            'department': 'Phụ Sản',
            'symptom_keywords': json.dumps([
                'đau bụng dưới', 'đau vùng chậu', 'đau bụng kinh',
                'đau buồng trứng'
            ], ensure_ascii=False),
            'priority': 6,
            'min_symptoms_match': 1,
            'esi_level_default': 3,
            'follow_up_questions': json.dumps([
                'Bạn có đang mang thai không?',
                'Đau có liên quan đến chu kỳ kinh không?',
                'Có ra máu bất thường không?'
            ], ensure_ascii=False),
            'additional_notes': 'Pelvic pain - rule out ectopic pregnancy if pregnant'
        },
        {
            'rule_name': 'Rối loạn kinh nguyệt',
            'department': 'Phụ Sản',
            'symptom_keywords': json.dumps([
                'trễ kinh', 'rối loạn kinh', 'kinh không đều',
                'ra máu bất thường', 'ra máu ngoài chu kỳ'
            ], ensure_ascii=False),
            'priority': 5,
            'min_symptoms_match': 1,
            'esi_level_default': 4,
            'follow_up_questions': json.dumps([
                'Chu kỳ kinh bình thường là bao lâu?',
                'Lần kinh cuối là khi nào?',
                'Có khả năng mang thai không?'
            ], ensure_ascii=False),
            'additional_notes': 'Menstrual irregularities'
        },
        {
            'rule_name': 'Thai nghén',
            'department': 'Phụ Sản',
            'symptom_keywords': json.dumps([
                'mang thai', 'có thai', 'khám thai', 'thai nghén',
                'test thai dương tính'
            ], ensure_ascii=False),
            'priority': 7,
            'min_symptoms_match': 1,
            'esi_level_default': 3,
            'follow_up_questions': json.dumps([
                'Thai được bao nhiêu tuần?',
                'Có triệu chứng bất thường nào không?',
                'Đây là lần khám thai đầu tiên?'
            ], ensure_ascii=False),
            'additional_notes': 'Prenatal care'
        },

        # ==================== NHI KHOA ====================
        {
            'rule_name': 'Sốt ở trẻ em',
            'department': 'Nhi Khoa',
            'symptom_keywords': json.dumps([
                'sốt', 'nóng sốt', 'sốt cao', 'con sốt',
                'bé sốt', 'trẻ sốt'
            ], ensure_ascii=False),
            'priority': 8,
            'min_symptoms_match': 1,
            'esi_level_default': 3,
            'follow_up_questions': json.dumps([
                'Bé bao nhiêu tuổi (hoặc tháng tuổi)?',
                'Sốt bao nhiêu độ?',
                'Có co giật, khóc thét, hoặc li bì không?'
            ], ensure_ascii=False),
            'additional_notes': 'Fever in children - assess age and severity'
        },
        {
            'rule_name': 'Ho + Sổ mũi trẻ em',
            'department': 'Nhi Khoa',
            'symptom_keywords': json.dumps([
                'ho', 'ho có đờm', 'khò khè', 'thở khó',
                'viêm phế quản', 'viêm phổi'
            ], ensure_ascii=False),
            'priority': 7,
            'min_symptoms_match': 1,
            'esi_level_default': 3,
            'follow_up_questions': json.dumps([
                'Bé bao nhiêu tuổi?',
                'Ho kéo dài bao lâu?',
                'Có khó thở, thở nhanh, rút lõm ngực không?'
            ], ensure_ascii=False),
            'additional_notes': 'Respiratory infection in children'
        },
        {
            'rule_name': 'Tiêu chảy trẻ em',
            'department': 'Nhi Khoa',
            'symptom_keywords': json.dumps([
                'tiêu chảy', 'ỉa chảy', 'đi ngoài lỏng',
                'nôn', 'nôn mửa'
            ], ensure_ascii=False),
            'priority': 7,
            'min_symptoms_match': 1,
            'esi_level_default': 3,
            'follow_up_questions': json.dumps([
                'Bé bao nhiêu tuổi?',
                'Đi ngoài mấy lần trong ngày?',
                'Có dấu hiệu mất nước không? (khóc không ra nước mắt, môi khô)'
            ], ensure_ascii=False),
            'additional_notes': 'Gastroenteritis - assess dehydration'
        },

        # ==================== TIÊU HÓA ====================
        {
            'rule_name': 'Đau bụng + Buồn nôn',
            'department': 'Tiêu Hóa',
            'symptom_keywords': json.dumps([
                'đau bụng', 'đau dạ dày', 'đau tức bụng',
                'buồn nôn', 'nôn', 'trào ngược'
            ], ensure_ascii=False),
            'priority': 6,
            'min_symptoms_match': 1,
            'esi_level_default': 3,
            'follow_up_questions': json.dumps([
                'Đau ở vị trí nào? (bụng trên, dưới, hai bên)',
                'Đau có liên quan đến ăn uống không?',
                'Có nôn ra máu hoặc phân đen không?'
            ], ensure_ascii=False),
            'additional_notes': 'Abdominal pain - assess location and severity'
        },
        {
            'rule_name': 'Tiêu chảy + Đi ngoài',
            'department': 'Tiêu Hóa',
            'symptom_keywords': json.dumps([
                'tiêu chảy', 'ỉa chảy', 'đi ngoài lỏng',
                'phân lỏng', 'táo bón'
            ], ensure_ascii=False),
            'priority': 5,
            'min_symptoms_match': 1,
            'esi_level_default': 4,
            'follow_up_questions': json.dumps([
                'Đi ngoài mấy lần trong ngày?',
                'Có máu hoặc nhầy trong phân không?',
                'Có ăn gì bất thường không?'
            ], ensure_ascii=False),
            'additional_notes': 'Diarrhea - rule out serious causes'
        },
        {
            'rule_name': 'Ợ nóng + Trào ngược',
            'department': 'Tiêu Hóa',
            'symptom_keywords': json.dumps([
                'ợ nóng', 'ợ chua', 'trào ngược', 'nóng rát dạ dày',
                'khó tiêu', 'đầy hơi'
            ], ensure_ascii=False),
            'priority': 4,
            'min_symptoms_match': 1,
            'esi_level_default': 4,
            'follow_up_questions': json.dumps([
                'Triệu chứng xuất hiện khi nào? (sau ăn, khi nằm)',
                'Có nuốt khó hoặc đau ngực không?',
                'Đã kéo dài bao lâu?'
            ], ensure_ascii=False),
            'additional_notes': 'GERD - gastroesophageal reflux disease'
        }
    ]

    print("Seeding symptom_rules table...")
    for rule in symptom_rules:
        dept_id = dept_map[rule['department']]
        cursor.execute("""
            INSERT INTO symptom_rules (
                rule_name, department_id, symptom_keywords, priority,
                min_symptoms_match, esi_level_default, follow_up_questions,
                additional_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rule['rule_name'], dept_id, rule['symptom_keywords'],
            rule['priority'], rule['min_symptoms_match'],
            rule['esi_level_default'], rule['follow_up_questions'],
            rule['additional_notes']
        ))

    print(f"✅ Added {len(symptom_rules)} symptom rules")


def seed_red_flags(cursor):
    """
    Seed red flags - Các dấu hiệu cảnh báo nguy hiểm
    """
    red_flags = [
        {
            'flag_name': 'Đau ngực cấp tính - Nguy cơ tim',
            'symptom_pattern': json.dumps({
                'primary': ['đau ngực', 'đau tim'],
                'secondary': ['lan ra tay trái', 'đổ mồ hôi lạnh', 'khó thở', 'buồn nôn'],
                'severity': 'severe',
                'duration': 'acute'
            }, ensure_ascii=False),
            'esi_level': 1,
            'action': 'emergency',
            'warning_message': '🚨 CẤP CỨU NGAY! Đau ngực có thể là dấu hiệu nhồi máu cơ tim. Đi CÂP CỨU NGAY hoặc gọi 115!',
            'recommended_department': 'Cấp Cứu - Tim Mạch',
            'age_constraint': None,
            'description': 'Acute chest pain - possible acute coronary syndrome'
        },
        {
            'flag_name': 'Khó thở nghiêm trọng',
            'symptom_pattern': json.dumps({
                'primary': ['khó thở', 'thở không ra hơi', 'ngạt thở'],
                'secondary': ['tím môi', 'vật vã', 'không nói được'],
                'severity': 'severe respiratory distress'
            }, ensure_ascii=False),
            'esi_level': 1,
            'action': 'emergency',
            'warning_message': '🚨 CẤP CỨU NGAY! Khó thở nghiêm trọng đe dọa tính mạng. Đến CÂP CỨU NGAY hoặc gọi 115!',
            'recommended_department': 'Cấp Cứu',
            'age_constraint': None,
            'description': 'Severe respiratory distress - immediate airway management needed'
        },
        {
            'flag_name': 'Sốt cao ở trẻ < 3 tháng',
            'symptom_pattern': json.dumps({
                'primary': ['sốt'],
                'age': '<3 months',
                'temperature': '>38°C',
                'severity': 'any fever in infant'
            }, ensure_ascii=False),
            'esi_level': 2,
            'action': 'urgent',
            'warning_message': '⚠️ KHẨN CẤP! Sốt ở trẻ dưới 3 tháng tuổi rất nguy hiểm. Cần khám NGAY trong vòng 30 phút!',
            'recommended_department': 'Nhi Khoa - Khẩn Cấp',
            'age_constraint': json.dumps({'max_age': '3 months'}, ensure_ascii=False),
            'description': 'Fever in infant <3 months - high risk of serious bacterial infection'
        },
        {
            'flag_name': 'Đau bụng dữ dội',
            'symptom_pattern': json.dumps({
                'primary': ['đau bụng dữ dội', 'đau bụng như dao đâm'],
                'secondary': ['bụng cứng', 'không dám cử động', 'nôn ra máu'],
                'severity': 'severe'
            }, ensure_ascii=False),
            'esi_level': 2,
            'action': 'urgent',
            'warning_message': '⚠️ KHẨN CẤP! Đau bụng dữ dội có thể là dấu hiệu bệnh nặng. Đi CÂP CỨU ngay!',
            'recommended_department': 'Cấp Cứu - Tiêu Hóa',
            'age_constraint': None,
            'description': 'Acute abdomen - possible surgical emergency'
        },
        {
            'flag_name': 'Chảy máu âm đạo + Thai nghén',
            'symptom_pattern': json.dumps({
                'primary': ['chảy máu âm đạo', 'ra máu nhiều'],
                'secondary': ['đau bụng dưới dữ dội'],
                'context': 'pregnant',
                'severity': 'urgent'
            }, ensure_ascii=False),
            'esi_level': 2,
            'action': 'urgent',
            'warning_message': '⚠️ KHẨN CẤP! Chảy máu khi mang thai rất nguy hiểm. Đi KHOA PHỤ SẢN CẤP CỨU ngay!',
            'recommended_department': 'Phụ Sản - Cấp Cứu',
            'age_constraint': json.dumps({'female_only': True}, ensure_ascii=False),
            'description': 'Vaginal bleeding in pregnancy - rule out ectopic or miscarriage'
        },
        {
            'flag_name': 'Khó thở + Sưng môi lưỡi (Dị ứng)',
            'symptom_pattern': json.dumps({
                'primary': ['sưng môi', 'sưng lưỡi', 'sưng họng'],
                'secondary': ['khó thở', 'khó nuốt', 'nổi mề đay'],
                'onset': 'rapid after exposure',
                'severity': 'anaphylaxis'
            }, ensure_ascii=False),
            'esi_level': 1,
            'action': 'emergency',
            'warning_message': '🚨 CẤP CỨU NGAY! Phản ứng dị ứng nặng (sốc phản vệ). Gọi 115 và đến CÂP CỨU NGAY!',
            'recommended_department': 'Cấp Cứu',
            'age_constraint': None,
            'description': 'Anaphylaxis - requires immediate epinephrine'
        },
        {
            'flag_name': 'Co giật ở trẻ em',
            'symptom_pattern': json.dumps({
                'primary': ['co giật', 'giật cứng', 'động kinh'],
                'context': 'pediatric',
                'severity': 'seizure'
            }, ensure_ascii=False),
            'esi_level': 2,
            'action': 'urgent',
            'warning_message': '⚠️ KHẨN CẤP! Co giật ở trẻ em cần xử lý ngay. Đến KHOA NHI - CÂP CỨU ngay!',
            'recommended_department': 'Nhi Khoa - Cấp Cứu',
            'age_constraint': json.dumps({'max_age': '16 years'}, ensure_ascii=False),
            'description': 'Seizure in children - requires immediate evaluation'
        },
        {
            'flag_name': 'Đột quỵ - Tê liệt nửa người',
            'symptom_pattern': json.dumps({
                'primary': ['tê nửa người', 'liệt nửa người', 'méo miệng'],
                'secondary': ['nói khó', 'nhìn đôi', 'đau đầu dữ dội'],
                'onset': 'sudden',
                'severity': 'stroke symptoms'
            }, ensure_ascii=False),
            'esi_level': 1,
            'action': 'emergency',
            'warning_message': '🚨 CẤP CỨU NGAY! Dấu hiệu đột quỵ - thời gian là vàng! Gọi 115 và đến CÂP CỨU NGAY!',
            'recommended_department': 'Cấp Cứu - Thần Kinh',
            'age_constraint': None,
            'description': 'Stroke symptoms - golden hour for intervention'
        }
    ]

    print("Seeding red_flags table...")
    for flag in red_flags:
        cursor.execute("""
            INSERT INTO red_flags (
                flag_name, symptom_pattern, esi_level, action,
                warning_message, recommended_department, age_constraint,
                description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flag['flag_name'], flag['symptom_pattern'], flag['esi_level'],
            flag['action'], flag['warning_message'], flag['recommended_department'],
            flag['age_constraint'], flag['description']
        ))

    print(f"✅ Added {len(red_flags)} red flags")


def verify_seed_data(cursor):
    """
    Verify seeded data
    """
    print("\n" + "="*60)
    print("Verifying seeded data...")
    print("="*60)

    cursor.execute("SELECT COUNT(*) FROM departments")
    dept_count = cursor.fetchone()[0]
    print(f"  Departments: {dept_count}")

    cursor.execute("SELECT COUNT(*) FROM symptom_rules")
    rules_count = cursor.fetchone()[0]
    print(f"  Symptom Rules: {rules_count}")

    cursor.execute("SELECT COUNT(*) FROM red_flags")
    flags_count = cursor.fetchone()[0]
    print(f"  Red Flags: {flags_count}")

    cursor.execute("SELECT COUNT(*) FROM conversations")
    conv_count = cursor.fetchone()[0]
    print(f"  Conversations: {conv_count}")

    # List departments
    print("\n📋 Danh sách chuyên khoa:")
    cursor.execute("SELECT name_vi, room_number, floor FROM departments")
    for name, room, floor in cursor.fetchall():
        print(f"   - {name} ({room}, {floor})")

    print("="*60)


def main():
    """
    Main function
    """
    print("\n" + "="*60)
    print("🌱 Starting Database Seeding - Demo Version")
    print("="*60)
    print(f"📁 Database path: {DB_PATH}\n")

    if not DB_PATH.exists():
        print("❌ Error: Database file not found!")
        print("💡 Please run init_db.py first to create the database")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Clear existing data
        print("🗑️  Clearing existing data...")
        cursor.execute("DELETE FROM conversations")
        cursor.execute("DELETE FROM red_flags")
        cursor.execute("DELETE FROM symptom_rules")
        cursor.execute("DELETE FROM departments")
        print("✅ Old data cleared\n")

        # Seed all tables
        seed_departments(cursor)
        seed_symptom_rules(cursor)
        seed_red_flags(cursor)

        conn.commit()
        verify_seed_data(cursor)

        print("\n✨ Database seeding completed successfully!")
        print("="*60 + "\n")

    except sqlite3.IntegrityError as e:
        print(f"\n⚠️ Integrity Error: {e}")
        print("💡 Data may already exist. Check the error message above.")
        conn.rollback()

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
