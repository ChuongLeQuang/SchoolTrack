import pytest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication
from apps.main_app.src.views.student_view import StudentView


@pytest.fixture(scope="session")
def qapp():
    """
    EN: Create a QApplication instance for tests (Singleton).
    VI: Tạo phiên bản QApplication duy nhất cho các kiểm thử giao diện.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@patch("apps.main_app.src.views.student_view.StudentService.get_students_from_excel")
def test_student_view_initialization(mock_get_students, qapp):
    """
    EN: Test if StudentView initializes and has correct table columns.
    VI: Kiểm thử xem StudentView có khởi tạo đúng và đủ cột bảng hay không.
    """
    mock_get_students.return_value = []
    view = StudentView()
    
    # Kiểm tra số lượng cột của bảng
    assert view.table.columnCount() == 8
    # Kiểm tra xem ô tìm kiếm có tồn tại không
    assert view.search_input.placeholderText() == "🔍 Tìm theo MSV, Họ, Tên..."


@patch("apps.main_app.src.views.student_view.StudentService.get_students_from_excel")
def test_student_view_filter(mock_get_students, qapp):
    """
    EN: Test search and filter functionality in StudentView.
    VI: Kiểm thử chức năng tìm kiếm và lọc trong StudentView.
    """
    from apps.main_app.src.models.entities import Student
    from datetime import date
    
    mock_get_students.return_value = [
        Student(student_id="SV01", full_name="Nguyen Van A", date_of_birth=date(2000, 1, 1), email="", phone_number="", study_status="Đang học"),
        Student(student_id="SV02", full_name="Tran Thi B", date_of_birth=date(2000, 1, 1), email="", phone_number="", study_status="Nghỉ học")
    ]
    
    view = StudentView()
    view.load_data()  # Ép tải dữ liệu ngay lập tức để test
    
    # Kiểm tra tìm kiếm bằng text (Gõ SV01 -> Dòng 1 hiện, Dòng 2 ẩn)
    view.search_input.setText("SV01")
    assert not view.table.isRowHidden(0)
    assert view.table.isRowHidden(1)
    
    # Kiểm tra bộ lọc trạng thái (Xóa text cũ, Chọn "Nghỉ học" -> Dòng 1 ẩn, Dòng 2 hiện)
    view.search_input.setText("")
    view.status_filter.setCurrentText("Nghỉ học")
    assert view.table.isRowHidden(0)
    assert not view.table.isRowHidden(1)