import pytest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDate
from apps.main_app.src.views.class_dialog import ClassDialog


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@patch("apps.main_app.src.views.class_dialog.ConfigService.get_class_templates")
@patch("apps.main_app.src.views.class_dialog.ConfigService.get_locations")
@patch("apps.main_app.src.views.class_dialog.ConfigService.get_sessions")
@patch("apps.main_app.src.views.class_dialog.ConfigService.get_schedules")
@patch("apps.main_app.src.views.class_dialog.ConfigService.get_time_slots")
def test_class_dialog_auto_generate_code(mock_get_time_slots, mock_get_schedules, mock_get_sessions, mock_get_locations, mock_get_templates, qapp) -> None:
    """
    EN: Test auto-generation of class code based on template and date.
    VI: Kiểm thử chức năng tự động sinh mã lớp dự kiến dựa trên mẫu và ngày tháng.
    """
    mock_get_templates.return_value = {
        "NE": {"name": "Level 1", "min": 15, "max": 30, "session": "Tối", "schedule": "2-4-6", "time_slot": "18:00 - 20:00", "location": "Cơ sở Q9"}
    }
    mock_get_locations.return_value = ["Cơ sở Q9"]
    mock_get_sessions.return_value = ["Sáng", "Tối"]
    mock_get_schedules.return_value = ["2-4-6"]
    mock_get_time_slots.return_value = ["08:00 - 10:00", "18:00 - 20:00"]
    
    # Giả lập trên bảng đã có sẵn lớp A và B của tháng 08/2025
    existing_codes = ["LNH0825NEA", "LNH0825NEB"]
    dialog = ClassDialog(existing_codes=existing_codes)
    
    dialog.cb_template.setCurrentIndex(1) # Chọn Template "NE"
    dialog.date_start.setDate(QDate(2025, 8, 1)) # Cài đặt khai giảng Tháng 08/2025
    
    assert dialog.txt_code.text() == "LNH0825NEC"  # Phải tự động tăng lên C
    assert dialog.txt_name.text() == "Level 1"
    assert dialog.sb_min.value() == 15
    
    # Kiểm tra tính năng tự động gợi ý Giờ học khi đổi Buổi học
    dialog.cb_session.setCurrentText("Sáng")
    assert "08:00" in dialog.cb_time_slot.currentText()