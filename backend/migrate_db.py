# migrate_db.py - Migrate database schema for SQL Server 2020

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

def migrate_database():
    """Update database schema to match chatbot service requirements"""
    print("=" * 60)
    print("Database Migration for SQL Server 2020")
    print("=" * 60)

    try:
        # 1. Drop and recreate conversations table with correct schema
        print("\n1. Updating 'conversations' table...")

        # Drop existing table
        try:
            Database.execute_update("DROP TABLE conversations")
            print("   Dropped old conversations table")
        except Exception as e:
            print(f"   Note: {e}")

        # Create new conversations table
        create_conversations = """
        CREATE TABLE conversations (
            id INT IDENTITY(1,1) PRIMARY KEY,
            session_id NVARCHAR(100) NOT NULL,
            turn_number INT NOT NULL DEFAULT 1,
            user_message NVARCHAR(MAX),
            bot_response NVARCHAR(MAX),
            extracted_symptoms NVARCHAR(MAX),
            current_esi_level INT,
            matched_red_flags NVARCHAR(MAX),
            recommended_department_id INT,
            conversation_status NVARCHAR(50) DEFAULT 'in_progress',
            patient_age INT,
            patient_gender NVARCHAR(10),
            timestamp DATETIME DEFAULT GETDATE(),
            created_at DATETIME DEFAULT GETDATE(),
            FOREIGN KEY (recommended_department_id) REFERENCES departments(id)
        )
        """
        Database.execute_update(create_conversations)
        print("   Created new conversations table")

        # Create index on session_id
        Database.execute_update("""
            CREATE INDEX idx_conversations_session ON conversations(session_id)
        """)
        print("   Created index on session_id")

        # 2. Add is_active column to symptom_rules if missing
        print("\n2. Updating 'symptom_rules' table...")
        try:
            Database.execute_update("""
                ALTER TABLE symptom_rules ADD is_active BIT DEFAULT 1
            """)
            print("   Added is_active column")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   is_active column already exists")
            else:
                print(f"   Note: {e}")

        # Update all existing rules to active
        Database.execute_update("UPDATE symptom_rules SET is_active = 1 WHERE is_active IS NULL")
        print("   Set all existing rules to active")

        # 3. Add is_active column to red_flags if missing
        print("\n3. Updating 'red_flags' table...")
        try:
            Database.execute_update("""
                ALTER TABLE red_flags ADD is_active BIT DEFAULT 1
            """)
            print("   Added is_active column")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   is_active column already exists")
            else:
                print(f"   Note: {e}")

        # Update all existing flags to active
        Database.execute_update("UPDATE red_flags SET is_active = 1 WHERE is_active IS NULL")
        print("   Set all existing flags to active")

        # 4. Add is_active column to departments if missing
        print("\n4. Updating 'departments' table...")
        try:
            Database.execute_update("""
                ALTER TABLE departments ADD is_active BIT DEFAULT 1
            """)
            print("   Added is_active column")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                print("   is_active column already exists")
            else:
                print(f"   Note: {e}")

        # Update all existing departments to active
        Database.execute_update("UPDATE departments SET is_active = 1 WHERE is_active IS NULL")
        print("   Set all existing departments to active")

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\nMigration FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    migrate_database()
