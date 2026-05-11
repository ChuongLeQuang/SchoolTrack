import pytest
from PyQt6.QtWidgets import QApplication
from apps.main_app.src.views.main_window import MainWindow


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


def test_main_window_initialization(qapp):
    """
    EN: Test if MainWindow initializes correctly with the correct title.
    VI: Kiểm thử xem MainWindow có khởi tạo đúng tiêu đề không.
    """
    window = MainWindow()
    assert window.windowTitle() == "SchoolTrack - Quản lý Lớp học"