"""
conversation.py - Model cho bảng conversations
Quản lý lịch sử hội thoại của người dùng
"""

import json
from models.database import Database
from datetime import datetime


class Conversation:
    """
    Model đại diện cho một cuộc hội thoại
    """

    @staticmethod
    def create(session_id, turn_number, user_message, bot_response,
               extracted_symptoms=None, opqrst_data=None, current_esi_level=None,
               matched_red_flags=None, recommended_department_id=None,
               conversation_status='in_progress', patient_age=None, patient_gender=None):
        """
        Tạo một record conversation mới

        Args:
            session_id (str): ID của session
            turn_number (int): Số thứ tự của turn
            user_message (str): Tin nhắn từ người dùng
            bot_response (str): Phản hồi từ bot
            extracted_symptoms (list): Danh sách triệu chứng đã trích xuất
            opqrst_data (dict): Dữ liệu OPQRST
            current_esi_level (int): Mức ESI hiện tại
            matched_red_flags (list): Danh sách red flags đã match
            recommended_department_id (int): ID khoa được đề xuất
            conversation_status (str): Trạng thái hội thoại
            patient_age (int): Tuổi bệnh nhân
            patient_gender (str): Giới tính bệnh nhân

        Returns:
            int: ID của conversation vừa tạo
        """
        query = """
        INSERT INTO conversations (
            session_id, turn_number, user_message, bot_response,
            extracted_symptoms, opqrst_data, current_esi_level,
            matched_red_flags, recommended_department_id,
            conversation_status, patient_age, patient_gender
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            session_id,
            turn_number,
            user_message,
            bot_response,
            json.dumps(extracted_symptoms, ensure_ascii=False) if extracted_symptoms else None,
            json.dumps(opqrst_data, ensure_ascii=False) if opqrst_data else None,
            current_esi_level,
            json.dumps(matched_red_flags, ensure_ascii=False) if matched_red_flags else None,
            recommended_department_id,
            conversation_status,
            patient_age,
            patient_gender
        )

        return Database.execute_update(query, params)

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
        query = """
        SELECT * FROM conversations
        WHERE session_id = ?
        ORDER BY turn_number ASC
        LIMIT ?
        """
        return Database.execute_query(query, (session_id, limit))

    @staticmethod
    def get_latest_turn(session_id):
        """
        Lấy turn mới nhất của session

        Args:
            session_id (str): ID của session

        Returns:
            dict: Turn mới nhất hoặc None
        """
        query = """
        SELECT * FROM conversations
        WHERE session_id = ?
        ORDER BY turn_number DESC
        LIMIT 1
        """
        return Database.execute_query(query, (session_id,), fetch_one=True)

    @staticmethod
    def get_turn_count(session_id):
        """
        Đếm số turn của session

        Args:
            session_id (str): ID của session

        Returns:
            int: Số turn
        """
        query = """
        SELECT COUNT(*) as count FROM conversations
        WHERE session_id = ?
        """
        result = Database.execute_query(query, (session_id,), fetch_one=True)
        return result['count'] if result else 0

    @staticmethod
    def delete_by_session(session_id):
        """
        Xóa tất cả conversation của một session

        Args:
            session_id (str): ID của session

        Returns:
            int: Số lượng row bị xóa
        """
        query = "DELETE FROM conversations WHERE session_id = ?"
        return Database.execute_update(query, (session_id,))

    @staticmethod
    def update_status(session_id, status):
        """
        Cập nhật trạng thái của conversation

        Args:
            session_id (str): ID của session
            status (str): Trạng thái mới

        Returns:
            int: Số row bị ảnh hưởng
        """
        query = """
        UPDATE conversations
        SET conversation_status = ?
        WHERE session_id = ?
        """
        return Database.execute_update(query, (status, session_id))
