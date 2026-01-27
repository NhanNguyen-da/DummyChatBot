"""
init_db.py - Database Initialization for Medical Triage Chatbot (SQL Server)
Tables: departments, symptom_rules, red_flags, conversations, quick_reply_rules
"""

import pyodbc
import sys
import argparse

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

CONNECTION_STRING = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=Chatbot;"
    "Trusted_Connection=yes;"
)


def get_connection():
    """Get database connection."""
    conn = pyodbc.connect(CONNECTION_STRING)
    conn.autocommit = False
    return conn


def create_departments_table(cursor):
    """Create departments table."""
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='departments' AND xtype='U')
        CREATE TABLE departments (
            id INT PRIMARY KEY IDENTITY(1,1),
            name_vi NVARCHAR(200) NOT NULL,
            name_en NVARCHAR(200),
            room_number NVARCHAR(50) NOT NULL,
            floor NVARCHAR(50),
            building NVARCHAR(100),
            doctor_name NVARCHAR(200),
            description NVARCHAR(MAX),
            working_hours NVARCHAR(200),
            is_active BIT DEFAULT 1,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
    """)
    print("  [OK] Table 'departments' created")


def create_symptom_rules_table(cursor):
    """Create symptom_rules table for symptom-to-department mapping."""
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='symptom_rules' AND xtype='U')
        CREATE TABLE symptom_rules (
            id INT PRIMARY KEY IDENTITY(1,1),
            rule_name NVARCHAR(200) NOT NULL,
            department_id INT NOT NULL,
            symptom_keywords NVARCHAR(MAX) NOT NULL,
            priority INT DEFAULT 5,
            min_symptoms_match INT DEFAULT 1,
            esi_level_default INT DEFAULT 4,
            follow_up_questions NVARCHAR(MAX),
            additional_notes NVARCHAR(MAX),
            is_active BIT DEFAULT 1,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)
    print("  [OK] Table 'symptom_rules' created")


def create_red_flags_table(cursor):
    """Create red_flags table for critical/emergency symptoms."""
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='red_flags' AND xtype='U')
        CREATE TABLE red_flags (
            id INT PRIMARY KEY IDENTITY(1,1),
            flag_name NVARCHAR(200) NOT NULL,
            symptom_pattern NVARCHAR(MAX) NOT NULL,
            esi_level INT NOT NULL CHECK(esi_level IN (1, 2)),
            action NVARCHAR(100) NOT NULL,
            warning_message NVARCHAR(MAX) NOT NULL,
            recommended_department NVARCHAR(200),
            age_constraint NVARCHAR(MAX),
            description NVARCHAR(MAX),
            is_active BIT DEFAULT 1,
            created_at DATETIME DEFAULT GETDATE(),
            updated_at DATETIME DEFAULT GETDATE()
        )
    """)
    print("  [OK] Table 'red_flags' created")


def create_conversations_table(cursor):
    """Create conversations table for chat history."""
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='conversations' AND xtype='U')
        CREATE TABLE conversations (
            id INT PRIMARY KEY IDENTITY(1,1),
            session_id NVARCHAR(100) NOT NULL,
            turn_number INT NOT NULL,
            user_message NVARCHAR(MAX),
            bot_response NVARCHAR(MAX),
            extracted_symptoms NVARCHAR(MAX),
            current_esi_level INT,
            matched_red_flags NVARCHAR(MAX),
            recommended_department_id INT,
            conversation_status NVARCHAR(50) DEFAULT 'in_progress',
            patient_age INT,
            patient_gender NVARCHAR(20),
            timestamp DATETIME DEFAULT GETDATE(),
            created_at DATETIME DEFAULT GETDATE(),
            
            -- New columns for scoring system
            current_score FLOAT DEFAULT 0,
            is_pregnant BIT DEFAULT 0,
            is_pediatric BIT DEFAULT 0,
            is_severe BIT DEFAULT 0,
            collected_duration NVARCHAR(100),
            collected_location NVARCHAR(100),
            last_question_type NVARCHAR(50),
            
            FOREIGN KEY (recommended_department_id) REFERENCES departments(id)
        )
    """)
    print("  [OK] Table 'conversations' created")


def create_quick_reply_rules_table(cursor):
    """Create quick_reply_rules table for dynamic quick replies."""
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='quick_reply_rules' AND xtype='U')
        CREATE TABLE quick_reply_rules (
            id INT PRIMARY KEY IDENTITY(1,1),
            trigger_type NVARCHAR(50) NOT NULL,
            trigger_value NVARCHAR(100) NOT NULL,
            replies_json NVARCHAR(MAX) NOT NULL,
            priority INT DEFAULT 5,
            is_active BIT DEFAULT 1,
            created_at DATETIME DEFAULT GETDATE()
        )
    """)
    print("  [OK] Table 'quick_reply_rules' created")


def create_indexes(cursor):
    """Create indexes for performance optimization."""
    indexes = [
        ("idx_conversations_session", "conversations", "session_id, turn_number"),
        ("idx_conversations_timestamp", "conversations", "timestamp"),
        ("idx_conversations_status", "conversations", "conversation_status"),
        ("idx_symptom_rules_department", "symptom_rules", "department_id"),
        ("idx_symptom_rules_priority", "symptom_rules", "priority DESC"),
        ("idx_quick_reply_trigger", "quick_reply_rules", "trigger_type, trigger_value, is_active"),
    ]
    
    for index_name, table_name, columns in indexes:
        try:
            cursor.execute(f"""
                IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = '{index_name}')
                CREATE INDEX {index_name} ON {table_name}({columns})
            """)
            print(f"  [OK] Index '{index_name}' created")
        except pyodbc.Error as e:
            print(f"  [WARN] Index '{index_name}': {e}")


def seed_departments(cursor, force_reseed=False):
    """Insert department data (ENT, OB/GYN, Pediatrics)."""
    if force_reseed:
        # Delete child records first (FK constraint)
        cursor.execute("DELETE FROM symptom_rules")
        cursor.execute("DELETE FROM conversations WHERE recommended_department_id IS NOT NULL")
        cursor.execute("DELETE FROM departments")
        # Reset identity to start from 1
        cursor.execute("DBCC CHECKIDENT ('departments', RESEED, 0)")
        print("  [OK] Cleared existing departments data")
    else:
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM departments")
        if cursor.fetchone()[0] > 0:
            print("  [SKIP] Departments already have data")
            return
    
    departments = [
        ("Khoa Tai Mui Hong", "ENT Department", "P101", "1", "A", "BS. Mbappe", "Kham va dieu tri cac benh ve tai, mui, hong", "7:00 - 17:00"),
        ("Khoa San Phu Khoa", "Obstetrics & Gynecology", "P202", "2", "B", "BS. C. Ronaldo", "Kham va dieu tri cac benh phu khoa, thai san", "7:00 - 17:00"),
        ("Khoa Nhi", "Pediatrics Department", "P303", "3", "C", "BS. L. Messi", "Kham va dieu tri benh cho tre em duoi 15 tuoi", "7:00 - 17:00"),
    ]
    
    for dept in departments:
        cursor.execute("""
            INSERT INTO departments (name_vi, name_en, room_number, floor, building, doctor_name, description, working_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, dept)
    
    print(f"  [OK] Inserted {len(departments)} departments")


def seed_symptom_rules(cursor, force_reseed=False):
    """Insert symptom rules for 3 departments."""
    if force_reseed:
        cursor.execute("DELETE FROM symptom_rules")
        cursor.execute("DBCC CHECKIDENT ('symptom_rules', RESEED, 0)")
        print("  [OK] Cleared existing symptom_rules data")
    else:
        cursor.execute("SELECT COUNT(*) FROM symptom_rules")
        if cursor.fetchone()[0] > 0:
            print("  [SKIP] Symptom rules already have data")
            return
    
    # Format: (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions)
    rules = [
        # ENT Department (ID=1)
        ("Benh ve Tai", 1, '["dau tai", "u tai", "chay mu tai", "nghe kem", "o tai", "vung vung"]', 7, 1, 4,
         '["Dau mot ben tai hay hai ben?", "Co chay dich tu tai khong?", "Co tieng vung vung trong tai khong?"]'),
        ("Benh ve Mui", 1, '["nghet mui", "chay nuoc mui", "so mui", "viem mui", "viem xoang", "chay mau mui", "hat hoi"]', 7, 1, 4,
         '["Nghet mui da bao lau roi?", "Co chay nuoc mui khong?", "Co dau vung mat khong?"]'),
        ("Benh ve Hong", 1, '["dau hong", "khan tieng", "viem hong", "nuot dau", "ho", "soi mang"]', 7, 1, 4,
         '["Dau hong da may ngay?", "Co kho nuot khong?", "Co sot khong?"]'),
        ("Dau dau lien quan Tai Mui Hong", 1, '["dau dau", "nhuc dau", "dau nua dau", "dau vung tran", "chong mat"]', 5, 1, 4,
         '["Dau o vi tri nao tren dau?", "Co kem nghet mui hoac dau hong khong?"]'),

        # OB/GYN Department (ID=2)
        ("Van de Kinh nguyet", 2, '["kinh nguyet", "tre kinh", "mat kinh", "roi loan kinh", "dau bung kinh", "ra mau bat thuong"]', 8, 1, 4,
         '["Chu ky kinh nguyet cua ban the nao?", "Kinh cuoi cung la khi nao?"]'),
        ("Thai san", 2, '["mang thai", "co thai", "bau", "thai nghen", "vo oi"]', 9, 1, 3,
         '["Ban dang mang thai duoc bao nhieu tuan/thang?", "Co trieu chung gi bat thuong khong?"]'),
        ("Benh Phu khoa", 2, '["phu khoa", "ngua vung kin", "ra dich", "dau vung kin", "viem am dao", "viem phu khoa"]', 7, 1, 4,
         '["Co dich ra tu am dao khong?", "Dich co mau gi, mui the nao?"]'),
        ("Dau bung duoi - Phu khoa", 2, '["dau bung duoi", "dau ha vi", "dau tieu khung", "dau vung bung duoi"]', 6, 1, 4,
         '["Dau co lien quan den kinh nguyet khong?", "Co thai hoac dang mang thai khong?"]'),

        # Pediatrics Department (ID=3)
        ("Sot o tre em", 3, '["sot", "nong nguoi", "sot cao", "sot nhe", "be sot", "con sot"]', 9, 1, 3,
         '["Be may tuoi?", "Sot bao nhieu do?", "Sot da may ngay?"]'),
        ("Ho o tre em", 3, '["ho", "ho nhieu", "ho khan", "ho co dom", "kho tho", "tho kho"]', 8, 1, 4,
         '["Ho da bao lau?", "Be co kho tho khong?", "Ho co dom xanh hoac vang khong?"]'),
        ("Tieu chay o tre em", 3, '["tieu chay", "di ngoai nhieu", "phan long", "non", "non mua", "tieu chay non"]', 8, 1, 4,
         '["Di ngoai may lan trong ngay?", "Co mau hoac nhat trong phan khong?", "Be con bu tot khong?"]'),
        ("Phat ban o tre em", 3, '["phat ban", "noi man", "noi sot", "ngua", "do da", "me day"]', 7, 1, 4,
         '["Ban o vi tri nao?", "Co sot kem khong?", "Be co ngua nhieu khong?"]'),
        ("Bo an/bu o tre em", 3, '["bo an", "bo bu", "an kem", "be quay", "khoc nhieu", "li bi"]', 8, 1, 3,
         '["Be may tuoi?", "Da bo an/bu bao lau?", "Co sot hoac tieu chay kem khong?"]'),
    ]
    
    for rule in rules:
        cursor.execute("""
            INSERT INTO symptom_rules (rule_name, department_id, symptom_keywords, priority, min_symptoms_match, esi_level_default, follow_up_questions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, rule)
    
    print(f"  [OK] Inserted {len(rules)} symptom rules")


def seed_red_flags(cursor, force_reseed=False):
    """Insert critical red flag patterns for emergencies."""
    if force_reseed:
        cursor.execute("DELETE FROM red_flags")
        cursor.execute("DBCC CHECKIDENT ('red_flags', RESEED, 0)")
        print("  [OK] Cleared existing red_flags data")
    else:
        cursor.execute("SELECT COUNT(*) FROM red_flags")
        if cursor.fetchone()[0] > 0:
            print("  [SKIP] Red flags already have data")
            return

    # Format: (flag_name, symptom_pattern, esi_level, action, warning_message, recommended_department, age_constraint, description)
    red_flags = [
        ("Cap cuu Thai san",
         '{"primary": ["ra mau", "chay mau", "xuat huyet"], "secondary": ["co that", "vo oi", "dau bung du doi"], "context": "pregnant"}',
         1, "emergency",
         "⚠️ CANH BAO KHAN CAP: Ban dang mang thai va co ra mau/chay mau. Vui long den Cap Cuu San Khoa ngay lap tuc hoac goi 115!",
         "Cap cuu San khoa", None, "Ra mau khi mang thai - nguy co say thai hoac sinh non"),

        ("Sot cao tre nho",
         '{"primary": ["sot cao", "sot"], "secondary": ["co giat", "li bi", "bo bu", "quay khoc"], "context": "pediatric"}',
         2, "urgent",
         "⚠️ KHAN CAP: Tre em bi sot cao can duoc kham ngay. Vui long dua be den Khoa Nhi trong vong 1-2 gio.",
         "Khoa Nhi", '{"max_age": 15}', "Sot cao o tre em - nguy co co giat hoac nhiem trung nang"),

        ("Kho tho nang tre em",
         '{"primary": ["kho tho", "tho kho", "tho nhanh"], "secondary": ["moi tim", "nguc co ro", "li bi"], "context": "pediatric"}',
         1, "emergency",
         "⚠️ CANH BAO KHAN CAP: Be co trieu chung kho tho nang. Vui long goi 115 hoac den Cap Cuu ngay lap tuc!",
         "Cap cuu", '{"max_age": 15}', "Kho tho nang o tre em - nguy co suy ho hap"),

        ("Dau bung du doi thai san",
         '{"primary": ["dau bung du doi", "dau bung nang"], "secondary": ["buon non", "chong mat"], "context": "pregnant"}',
         2, "urgent",
         "⚠️ KHAN CAP: Ban dang mang thai va co dau bung du doi. Vui long den Khoa San Phu Khoa trong vong 2 gio de kham.",
         "Khoa San Phu Khoa", None, "Dau bung du doi khi mang thai can kiem tra kip thoi"),

        ("Tai bien Tai Mui Hong",
         '{"primary": ["kho tho", "tho kho", "sung hong"], "secondary": ["khan giong", "khan tieng", "nuot kho"], "context": ""}',
         1, "emergency",
         "⚠️ CANH BAO KHAN CAP: Trieu chung cua ban co the gay nguy hiem duong tho. Vui long goi 115 hoac den Cap Cuu ngay!",
         "Cap cuu", None, "Sung hong/kho tho - nguy co tac duong tho"),
    ]
    
    for flag in red_flags:
        cursor.execute("""
            INSERT INTO red_flags (flag_name, symptom_pattern, esi_level, action, warning_message, recommended_department, age_constraint, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, flag)
    
    print(f"  [OK] Inserted {len(red_flags)} red flags")


def seed_quick_reply_rules(cursor, force_reseed=False):
    """Insert quick reply rules for dynamic quick replies."""
    if force_reseed:
        cursor.execute("DELETE FROM quick_reply_rules")
        cursor.execute("DBCC CHECKIDENT ('quick_reply_rules', RESEED, 0)")
        print("  [OK] Cleared existing quick_reply_rules data")
    else:
        cursor.execute("SELECT COUNT(*) FROM quick_reply_rules")
        if cursor.fetchone()[0] > 0:
            print("  [SKIP] Quick reply rules already have data")
            return

    # Format: (trigger_type, trigger_value, replies_json, priority)
    rules = [
        # Missing info
        ('missing_info', 'age', '[{"id": "age_1", "label": "Duoi 15 tuoi", "value": "Toi duoi 15 tuoi"}, {"id": "age_2", "label": "15-40 tuoi", "value": "Toi tu 15 den 40 tuoi"}, {"id": "age_3", "label": "41-65 tuoi", "value": "Toi tu 41 den 65 tuoi"}, {"id": "age_4", "label": "Tren 65 tuoi", "value": "Toi tren 65 tuoi"}]', 10),
        ('missing_info', 'gender', '[{"id": "gender_1", "label": "Nam", "value": "Toi la nam"}, {"id": "gender_2", "label": "Nu", "value": "Toi la nu"}]', 9),
        ('missing_info', 'duration', '[{"id": "dur_1", "label": "Hom nay", "value": "Moi bat dau hom nay"}, {"id": "dur_2", "label": "1-3 ngay", "value": "Duoc 1 den 3 ngay"}, {"id": "dur_3", "label": "Tren 1 tuan", "value": "Da hon 1 tuan"}, {"id": "dur_4", "label": "Tren 1 thang", "value": "Da hon 1 thang"}]', 8),
        ('missing_info', 'severity', '[{"id": "sev_1", "label": "Nhe", "value": "Muc do nhe, chiu duoc"}, {"id": "sev_2", "label": "Trung binh", "value": "Muc do trung binh, kho chiu"}, {"id": "sev_3", "label": "Nang", "value": "Muc do nang, rat kho chiu"}, {"id": "sev_4", "label": "Rat nang", "value": "Rat nang, khong chiu noi"}]', 7),
        # Context
        ('context', 'pregnant', '[{"id": "preg_1", "label": "Dau co that", "value": "Dau bung co that tung con"}, {"id": "preg_2", "label": "Ra mau", "value": "Co ra mau am dao"}, {"id": "preg_3", "label": "Ra dich bat thuong", "value": "Co ra dich bat thuong"}, {"id": "preg_4", "label": "Thai may it", "value": "Thai may it hon binh thuong"}]', 8),
        ('context', 'pediatric', '[{"id": "ped_1", "label": "Quay khoc nhieu", "value": "Be quay khoc nhieu, khong nin"}, {"id": "ped_2", "label": "Bo an/bu", "value": "Be bo an, bo bu"}, {"id": "ped_3", "label": "Non tro", "value": "Be non tro nhieu"}, {"id": "ped_4", "label": "Phat ban", "value": "Be co phat ban tren da"}]', 8),
        # Symptoms
        ('symptom', 'tai', '[{"id": "ear_1", "label": "Dau mot ben", "value": "Chi dau mot ben tai"}, {"id": "ear_2", "label": "Dau hai ben", "value": "Dau ca hai ben tai"}, {"id": "ear_3", "label": "Chay mu", "value": "Co chay mu tai"}, {"id": "ear_4", "label": "Nghe kem", "value": "Nghe kem, nghe khong ro"}]', 5),
        ('symptom', 'mui', '[{"id": "nose_1", "label": "Nghet mui", "value": "Bi nghet mui"}, {"id": "nose_2", "label": "Chay nuoc mui", "value": "Chay nuoc mui nhieu"}, {"id": "nose_3", "label": "Chay mau mui", "value": "Co chay mau mui"}, {"id": "nose_4", "label": "Dau vung mat", "value": "Dau vung mat, gan mui"}]', 5),
        ('symptom', 'hong', '[{"id": "throat_1", "label": "Dau hong", "value": "Dau hong, nuot dau"}, {"id": "throat_2", "label": "Khan tieng", "value": "Bi khan giong"}, {"id": "throat_3", "label": "Ho", "value": "Ho nhieu"}, {"id": "throat_4", "label": "Soi mang", "value": "Hong soi, do mang"}]', 5),
        ('symptom', 'sot', '[{"id": "fev_1", "label": "Sot cao >39°C", "value": "Sot cao tren 39 do"}, {"id": "fev_2", "label": "Sot nhe 37-38°C", "value": "Sot nhe khoang 37-38 do"}, {"id": "fev_3", "label": "Sot kem ho", "value": "Sot kem theo ho"}, {"id": "fev_4", "label": "Sot kem dau dau", "value": "Sot kem dau dau"}]', 5),
        ('symptom', 'kinh nguyet', '[{"id": "mens_1", "label": "Tre kinh", "value": "Kinh den tre"}, {"id": "mens_2", "label": "Roi loan", "value": "Kinh nguyet khong deu"}, {"id": "mens_3", "label": "Ra mau nhieu", "value": "Ra mau nhieu bat thuong"}, {"id": "mens_4", "label": "Dau bung kinh", "value": "Dau bung khi co kinh"}]', 5),
        ('symptom', 'ho', '[{"id": "cough_1", "label": "Ho khan", "value": "Ho khan, khong co dom"}, {"id": "cough_2", "label": "Ho co dom", "value": "Ho co dom"}, {"id": "cough_3", "label": "Ho ra mau", "value": "Ho co lan mau"}, {"id": "cough_4", "label": "Ho ve dem", "value": "Ho nhieu ve dem"}]', 5),
        # Default
        ('default', 'initial', '[{"id": "init_1", "label": "Tai Mui Hong", "value": "Toi bi van de ve tai, mui hoac hong"}, {"id": "init_2", "label": "San Phu Khoa", "value": "Toi co van de phu khoa hoac mang thai"}, {"id": "init_3", "label": "Benh tre em", "value": "Con toi bi benh, can kham Nhi khoa"}, {"id": "init_4", "label": "Khac", "value": "Toi co trieu chung khac"}]', 1),
    ]
    
    for rule in rules:
        cursor.execute("""
            INSERT INTO quick_reply_rules (trigger_type, trigger_value, replies_json, priority)
            VALUES (?, ?, ?, ?)
        """, rule)
    
    print(f"  [OK] Inserted {len(rules)} quick reply rules")


def verify_tables(cursor):
    """Verify all tables and show row counts."""
    cursor.execute("""
        SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME
    """)
    tables = cursor.fetchall()
    print("\n" + "=" * 50)
    print("DATABASE TABLES:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        print(f"  - {table[0]} ({cursor.fetchone()[0]} rows)")
    print("=" * 50)


def main():
    """Initialize database. Use --reseed to clear and re-insert data."""
    parser = argparse.ArgumentParser(description='Initialize Medical Triage Database')
    parser.add_argument('--reseed', action='store_true', help='Force reseed data')
    args = parser.parse_args()

    print("\n" + "=" * 50)
    print("DATABASE INITIALIZATION" + (" (RESEED)" if args.reseed else ""))
    print("=" * 50)

    conn = None
    try:
        print("\n[1] Connecting...")
        conn = get_connection()
        cursor = conn.cursor()
        print("  [OK] Connected")

        print("\n[2] Creating tables...")
        create_departments_table(cursor)
        create_symptom_rules_table(cursor)
        create_red_flags_table(cursor)
        create_conversations_table(cursor)
        create_quick_reply_rules_table(cursor)

        print("\n[3] Creating indexes...")
        create_indexes(cursor)
        conn.commit()

        print("\n[4] Inserting seed data...")
        seed_departments(cursor, force_reseed=args.reseed)
        seed_symptom_rules(cursor, force_reseed=args.reseed)
        seed_red_flags(cursor, force_reseed=args.reseed)
        seed_quick_reply_rules(cursor, force_reseed=args.reseed)
        conn.commit()

        print("\n[5] Verifying...")
        verify_tables(cursor)

        print("\n" + "=" * 50)
        print("COMPLETED SUCCESSFULLY!")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
