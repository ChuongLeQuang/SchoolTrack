import pytest
from datetime import date
from PyQt6.QtWidgets import QApplication
from apps.main_app.src.views.student_dialog import StudentDialog
from apps.main_app.src.models.entities import Student


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_student_dialog_add_mode(qapp):
    """
    EN: Test StudentDialog initialization in Add mode.
    VI: Kiểm thử khởi tạo StudentDialog ở chế độ Thêm.
    """
    dialog = StudentDialog()
    assert dialog.windowTitle() == "➕ Thêm Sinh viên Mới"
    assert not dialog.is_edit_mode
    assert not dialog.txt_id.isReadOnly()


def test_student_dialog_edit_mode(qapp):
    """
    EN: Test StudentDialog initialization and data loading in Edit mode.
    VI: Kiểm thử khởi tạo StudentDialog ở chế độ Sửa và nạp dữ liệu.
    """
    student = Student(
        student_id="SV01",
        full_name="Test Name",
        date_of_birth=date(2000, 1, 1),
        email="test@email.com",
        phone_number="0123",
        study_status="Đang học",
        tuition_balance=1000
    )
    dialog = StudentDialog(student=student)
    assert dialog.windowTitle() == "✏️ Sửa Thông tin Sinh viên"
    assert dialog.is_edit_mode
    assert dialog.txt_id.isReadOnly()
    assert dialog.txt_name.text() == "Test Name"
    
    data = dialog.get_student_data()
    assert data["student_id"] == "SV01"
    assert data["tuition_balance"] == 1000