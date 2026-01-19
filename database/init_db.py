"""
init_db.py - Database Initialization Script
Creates SQLite database tables for Medical Triage Chatbot

This script creates 4 main tables:
1. departments - Medical departments information
2. symptom_rules - Rules for matching symptoms to departments
3. red_flags - Critical symptoms requiring immediate attention
4. conversations - Chat history and patient interactions
"""

import sqlite3
import os
import sys
from pathlib import Path

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Get the database directory path
DB_DIR = Path(__file__).resolve().parent
DB_PATH = os.path.join(DB_DIR, 'chatbot.db')


def create_departments_table(cursor):
    """
    Create departments table to store medical department information

    Stores information about hospital departments including:
    - Department names (Vietnamese and English)
    - Location details (room, floor, building)
    - Doctor assignments
    - Working hours and descriptions
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_vi TEXT NOT NULL,
            name_en TEXT,
            room_number TEXT NOT NULL,
            floor TEXT,
            building TEXT,
            doctor_name TEXT,
            description TEXT,
            working_hours TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Table 'departments' created successfully")


def create_symptom_rules_table(cursor):
    """
    Create symptom_rules table to store symptom matching rules

    Stores rules that map symptom keywords to appropriate departments:
    - Symptom keywords (JSON array)
    - Priority levels for matching
    - Default ESI (Emergency Severity Index) levels
    - Follow-up questions to ask patients
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS symptom_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            symptom_keywords TEXT NOT NULL,
            priority INTEGER DEFAULT 5,
            min_symptoms_match INTEGER DEFAULT 1,
            esi_level_default INTEGER DEFAULT 4,
            follow_up_questions TEXT,
            additional_notes TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)
    print("✅ Table 'symptom_rules' created successfully")


def create_red_flags_table(cursor):
    """
    Create red_flags table to store critical symptom patterns

    Stores patterns that indicate emergency or urgent situations:
    - Critical symptom patterns (JSON object)
    - ESI levels 1 or 2 (most critical)
    - Action required (emergency/urgent)
    - Warning messages to display
    - Age constraints if applicable
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS red_flags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flag_name TEXT NOT NULL,
            symptom_pattern TEXT NOT NULL,
            esi_level INTEGER NOT NULL CHECK(esi_level IN (1, 2)),
            action TEXT NOT NULL,
            warning_message TEXT NOT NULL,
            recommended_department TEXT,
            age_constraint TEXT,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Table 'red_flags' created successfully")


def create_conversations_table(cursor):
    """
    Create conversations table to store chat history

    Stores all chatbot interactions with patients:
    - Session ID for tracking individual conversations
    - Turn-by-turn conversation data
    - Extracted symptoms and OPQRST data
    - ESI levels and red flag detections
    - Department recommendations
    - Patient demographics
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            turn_number INTEGER NOT NULL,
            user_message TEXT,
            bot_response TEXT,
            extracted_symptoms TEXT,
            opqrst_data TEXT,
            current_esi_level INTEGER,
            matched_red_flags TEXT,
            recommended_department_id INTEGER,
            conversation_status TEXT DEFAULT 'in_progress',
            patient_age INTEGER,
            patient_gender TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recommended_department_id) REFERENCES departments(id)
        )
    """)
    print("✅ Table 'conversations' created successfully")


def create_indexes(cursor):
    """
    Create database indexes for performance optimization

    Indexes improve query performance for:
    - Searching conversations by session
    - Time-based queries
    - Symptom rule lookups by department
    - Priority-based rule matching
    """
    # Index for conversation queries by session and turn
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_session
        ON conversations(session_id, turn_number)
    """)
    print("✅ Index 'idx_conversations_session' created successfully")

    # Index for time-based conversation queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversations_timestamp
        ON conversations(timestamp)
    """)
    print("✅ Index 'idx_conversations_timestamp' created successfully")

    # Index for symptom rule lookups by department
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_symptom_rules_department
        ON symptom_rules(department_id)
    """)
    print("✅ Index 'idx_symptom_rules_department' created successfully")

    # Index for priority-based symptom rule queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_symptom_rules_priority
        ON symptom_rules(priority DESC)
    """)
    print("✅ Index 'idx_symptom_rules_priority' created successfully")


def verify_tables(cursor):
    """
    Verify all tables were created successfully

    Queries the SQLite master table to list all created tables
    and displays them for verification
    """
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)

    tables = cursor.fetchall()
    print("\n" + "="*60)
    print("📋 Database Tables Created:")
    print("="*60)
    for table in tables:
        print(f"  - {table[0]}")
    print("="*60)

    # Also list indexes
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index'
        AND name LIKE 'idx_%'
        ORDER BY name
    """)

    indexes = cursor.fetchall()
    print("\n📊 Database Indexes Created:")
    print("="*60)
    for index in indexes:
        print(f"  - {index[0]}")
    print("="*60)


def main():
    """
    Main function to initialize the database

    Steps:
    1. Create database directory if not exists
    2. Connect to SQLite database
    3. Create all tables
    4. Create indexes
    5. Verify creation
    6. Commit and close connection
    """
    print("\n" + "="*60)
    print("🚀 Starting Database Initialization")
    print("="*60)
    print(f"📁 Database path: {DB_PATH}\n")

    # Ensure database directory exists
    os.makedirs(DB_DIR, exist_ok=True)

    # Connect to database (creates file if not exists)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Create all tables
        print("Creating tables...\n")
        create_departments_table(cursor)
        create_symptom_rules_table(cursor)
        create_red_flags_table(cursor)
        create_conversations_table(cursor)

        # Create indexes
        print("\nCreating indexes...\n")
        create_indexes(cursor)

        # Commit changes
        conn.commit()

        # Verify tables were created
        verify_tables(cursor)

        print("\n✨ Database initialization completed successfully!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error during database initialization: {str(e)}")
        conn.rollback()
        raise

    finally:
        # Close connection
        cursor.close()
        conn.close()


if __name__ == '__main__':
    main()
