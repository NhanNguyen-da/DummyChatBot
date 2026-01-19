"""
database.py - Module quản lý kết nối và thao tác với SQLite database
"""

import sqlite3
from contextlib import contextmanager
from config import Config

class Database:
    """
    Class quản lý database connection và operations
    """

    @staticmethod
    @contextmanager
    def get_connection():
        """
        Context manager để quản lý kết nối database

        Usage:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM departments")

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(Config.DATABASE_PATH)
            conn.row_factory = sqlite3.Row  # Để trả về dict thay vì tuple
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    @staticmethod
    def execute_query(query, params=None, fetch_one=False):
        """
        Thực thi một query và trả về kết quả

        Args:
            query (str): SQL query
            params (tuple): Parameters cho query
            fetch_one (bool): True nếu chỉ lấy 1 record

        Returns:
            dict hoặc list: Kết quả query
        """
        with Database.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None
            else:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]

    @staticmethod
    def execute_update(query, params=None):
        """
        Thực thi INSERT/UPDATE/DELETE query

        Args:
            query (str): SQL query
            params (tuple): Parameters cho query

        Returns:
            int: ID của row vừa insert (nếu là INSERT)
        """
        with Database.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.lastrowid
