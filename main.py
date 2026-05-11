import sys
from PyQt6.QtWidgets import QApplication
from apps.main_app.src.views.main_window import MainWindow


def main() -> None:
    """
    EN: Main entry point for the SchoolTrack application.
    VI: Điểm neo khởi chạy chính cho ứng dụng SchoolTrack.
    """
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()