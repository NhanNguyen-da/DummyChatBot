# check_tables.py - Check table structures in SQL Server

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import Database

def check_table_structure():
    """Check existing table structures"""
    print("=" * 60)
    print("Checking SQL Server Table Structures")
    print("=" * 60)

    # Get all tables
    query = """
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    """
    tables = Database.execute_query(query)
    print(f"\nFound {len(tables)} tables:")

    for table in tables:
        table_name = table['TABLE_NAME']
        print(f"\n{'='*40}")
        print(f"Table: {table_name}")
        print("-" * 40)

        # Get columns
        col_query = """
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """
        columns = Database.execute_query(col_query, (table_name,))

        for col in columns:
            col_type = col['DATA_TYPE']
            if col['CHARACTER_MAXIMUM_LENGTH']:
                col_type += f"({col['CHARACTER_MAXIMUM_LENGTH']})"
            nullable = "NULL" if col['IS_NULLABLE'] == 'YES' else "NOT NULL"
            print(f"  {col['COLUMN_NAME']:30} {col_type:20} {nullable}")

if __name__ == '__main__':
    check_table_structure()
