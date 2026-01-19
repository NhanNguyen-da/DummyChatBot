"""
conversation.py - Model cho bảng conversations
Quản lý lịch sử hội thoại của người dùng
"""

from models.database import Database
from datetime import datetime

class Conversation:
    """
    Model đại diện cho một cuộc hội thoại
    """

    @staticmethod
    def create(session_id, user_message, bot_response, suggested_department=None):
        """
        Tạo một record conversation mới

        Args:
            session_id (str): ID của session
            user_message (str): Tin nhắn từ người dùng
            bot_response (str): Phản hồi từ bot
            suggested_department (str): Khoa được đề xuất (nếu có)

        Returns:
            int: ID của conversation vừa tạo
        """
        # TODO: Implement insert to database
        query = """
        INSERT INTO conversations (session_id, user_message, bot_response, suggested_department, timestamp)
        VALUES (?, ?, ?, ?, ?)
        """
        timestamp = datetime.now().isoformat()
        return Database.execute_update(query, (session_id, user_message, bot_response, suggested_department, timestamp))

    @staticmethod
    def get_by_session(session_id, limit=10):
        """
        Lấy lịch sử hội thoại theo session_id

        Args:
            session_id (str): ID của session
            limit (int): Số lượng tin nhắn tối đa

        Returns:
            list: Danh sách các conversation
        """
        # TODO: Implement get from database
        query = """
        SELECT * FROM conversations
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        """
        return Database.execute_query(query, (session_id, limit))

    @staticmethod
    def delete_by_session(session_id):
        """
        Xóa tất cả conversation của một session

        Args:
            session_id (str): ID của session

        Returns:
            int: Số lượng row bị xóa
        """
        # TODO: Implement delete
        query = "DELETE FROM conversations WHERE session_id = ?"
        return Database.execute_update(query, (session_id,))
