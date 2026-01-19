"""
department_service.py - Service quản lý thông tin về các khoa
"""

from models.database import Database

class DepartmentService:
    """
    Service quản lý thông tin khoa/phòng khám
    """

    @staticmethod
    def get_all_departments():
        """
        Lấy tất cả các khoa

        Returns:
            list: Danh sách các khoa
        """
        query = "SELECT * FROM departments ORDER BY name"
        return Database.execute_query(query)

    @staticmethod
    def get_department_by_id(department_id):
        """
        Lấy thông tin một khoa theo ID

        Args:
            department_id (int): ID của khoa

        Returns:
            dict: Thông tin khoa
        """
        query = "SELECT * FROM departments WHERE id = ?"
        return Database.execute_query(query, (department_id,), fetch_one=True)

    @staticmethod
    def get_department_by_name(name):
        """
        Lấy thông tin khoa theo tên

        Args:
            name (str): Tên khoa

        Returns:
            dict: Thông tin khoa
        """
        query = "SELECT * FROM departments WHERE name LIKE ?"
        return Database.execute_query(query, (f"%{name}%",), fetch_one=True)

    @staticmethod
    def search_by_symptoms(symptoms):
        """
        Tìm kiếm khoa phù hợp dựa trên triệu chứng

        Args:
            symptoms (list): Danh sách triệu chứng

        Returns:
            list: Danh sách các khoa có thể phù hợp
        """
        # TODO: Implement search logic sử dụng bảng symptom_rules
        return []
