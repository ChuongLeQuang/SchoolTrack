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


@patch("apps.main_app.src.views.class_view.ClassService.get_classes_from_excel")
def test_class_view_initialization(mock_get_classes, qapp) -> None:
    """
    EN: Test ClassView initialization and table columns (including Checkbox).
    VI: Kiểm thử khởi tạo ClassView và kiểm tra cấu trúc 13 cột (có cột Chọn).
    """
    mock_get_classes.return_value = []
    view = ClassView()
    
    assert view.table.columnCount() == 13
    assert view.table.horizontalHeaderItem(0).text() == "Chọn"