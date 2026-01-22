# models/database.py

import pyodbc
from contextlib import contextmanager
import config

class Database:
    
    @staticmethod
    def get_connection_string():
        """Build connection string"""
        cfg = config.DB_CONFIG
        
        # Windows Authentication
        if cfg.get('trusted_connection'):
            return (
                f"DRIVER={{{cfg['driver']}}};"
                f"SERVER={cfg['server']};"
                f"DATABASE={cfg['database']};"
                f"Trusted_Connection=yes;"
            )
        
        # SQL Server Authentication
        return (
            f"DRIVER={{{cfg['driver']}}};"
            f"SERVER={cfg['server']};"
            f"DATABASE={cfg['database']};"
            f"UID={cfg['username']};"
            f"PWD={cfg['password']};"
        )
    
    @staticmethod
    @contextmanager
    def get_connection():
        """Context manager for database connection"""
        conn = None
        try:
            conn = pyodbc.connect(Database.get_connection_string())
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
        """Execute SELECT query"""
        with Database.get_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get column names
            columns = [column[0] for column in cursor.description]
            
            if fetch_one:
                row = cursor.fetchone()
                return dict(zip(columns, row)) if row else None
            else:
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
    
    @staticmethod
    def execute_update(query, params=None):
        """Execute INSERT/UPDATE/DELETE"""
        with Database.get_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get last inserted ID (SQL Server)
            cursor.execute("SELECT @@IDENTITY")
            result = cursor.fetchone()
            return result[0] if result else None