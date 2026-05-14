import pytest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication
from apps.main_app.src.views.class_view import ClassView


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@patch("apps.main_app.src.views.class_planning_tab.ClassService.get_classes_from_excel")
def test_class_view_initialization(mock_get_classes, qapp) -> None:
    """
    EN: Test ClassView initialization and table columns (including Checkbox).
    VI: Kiểm thử khởi tạo ClassView và kiểm tra cấu trúc 13 cột (có cột Chọn).
    """
    mock_get_classes.return_value = []
    view = ClassView()
    
    assert view.planning_tab.table.columnCount() == 13
    assert view.planning_tab.table.horizontalHeaderItem(0).text() == "Chọn"


@patch("apps.main_app.src.views.class_planning_tab.WaveMetadataService.get_class_codes_for_wave")
@patch("apps.main_app.src.views.class_planning_tab.ClassService.get_classes_from_excel")
@patch("os.path.exists")
def test_class_planning_tab_load_data(mock_exists, mock_get_classes, mock_get_codes, qapp) -> None:
    """
    EN: Test deep execution flow of load_data to catch AttributeErrors.
    VI: Kiểm thử luồng thực thi sâu của load_data để bắt lỗi thuộc tính.
    """
    mock_exists.return_value = True
    mock_get_classes.return_value = []
    mock_get_codes.return_value = []
    
    from apps.main_app.src.views.class_planning_tab import ClassPlanningTab
    tab = ClassPlanningTab()
    
    # Ép code phải chạy sâu qua các rẽ nhánh thay vì return sớm
    tab.load_data("2025-2026", "Đợt 1")
    
    # Nếu bị lỗi AttributeError, bài test sẽ fail ngay lập tức trước khi tới dòng này
    assert mock_get_classes.called