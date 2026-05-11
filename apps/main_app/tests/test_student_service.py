import pytest
from unittest.mock import patch
from datetime import date
from apps.main_app.src.models.entities import Student
from apps.main_app.src.services.student_service import StudentService


@patch("apps.main_app.src.services.excel_service.ExcelService.load_excel_data")
def test_get_students_from_excel_success(mock_load_excel):
    """
    EN: Test mapping Excel dictionary data to Student objects.
    VI: Kiểm thử chuyển đổi dữ liệu Excel (dict) sang đối tượng Student.
    """
    # Giả lập dữ liệu trả về từ ExcelService (đã được ép kiểu string)
    mock_load_excel.return_value = [
        {
            "Mã Sinh viên": "SV2026001",
            "Họ và tên": "Nguyễn Văn A",
            "Ngày sinh": "2005-08-15 00:00:00",  # Giả lập định dạng openpyxl thường parse
            "Email": "nva@gmail.com",
            "Số điện thoại": "0987654321",
            "Trạng thái học tập": "Đang học",
            "Số dư học phí": "5,000,000"
        }
    ]

    # Gọi hàm từ service
    students = StudentService.get_students_from_excel("fake_path.xlsx")

    # Kiểm tra tính đúng đắn của dữ liệu
    assert len(students) == 1
    
    student = students[0]
    assert isinstance(student, Student)
    assert student.student_id == "SV2026001"
    assert student.full_name == "Nguyễn Văn A"
    assert student.email == "nva@gmail.com"
    assert student.study_status == "Đang học"
    assert student.date_of_birth == date(2005, 8, 15)
    assert student.tuition_balance == 5000000


@patch("apps.main_app.src.services.excel_service.ExcelService.save_row")
def test_save_student_to_excel(mock_save_row):
    """
    EN: Test saving a Student object to Excel.
    VI: Kiểm thử lưu đối tượng Sinh viên xuống Excel.
    """
    student = Student(student_id="SV01", full_name="A", date_of_birth=date(2000, 1, 1), email="a@a.com", phone_number="123", study_status="Đang học", tuition_balance=10)
    StudentService.save_student_to_excel("fake.xlsx", student)
    mock_save_row.assert_called_once()
    args, kwargs = mock_save_row.call_args
    assert args[0] == "fake.xlsx"
    assert "Mã Sinh viên" in args[1]
    assert args[2] == "SV01"
    assert args[3][0][1] == "SV01"  # ID
    assert args[3][1][1] == "A"     # Họ và tên
    assert args[3][3][1] == "A"     # Tên (sau khi tách)