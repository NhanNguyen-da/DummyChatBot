"""
department_routes.py - Routes quản lý thông tin khoa/phòng
Chứa các endpoint để lấy thông tin về các khoa khám bệnh
"""

from flask import Blueprint, jsonify

# Tạo Blueprint cho department routes
department_bp = Blueprint('department', __name__)

@department_bp.route('/departments', methods=['GET'])
def get_all_departments():
    """
    Lấy danh sách tất cả các khoa

    Returns:
        JSON response với danh sách các khoa
    """
    # TODO: Implement get from database
    return jsonify({
        'departments': []
    }), 200

@department_bp.route('/departments/<int:department_id>', methods=['GET'])
def get_department(department_id):
    """
    Lấy thông tin chi tiết của một khoa

    Args:
        department_id (int): ID của khoa

    Returns:
        JSON response với thông tin khoa
    """
    # TODO: Implement get specific department
    return jsonify({
        'department': None
    }), 200
