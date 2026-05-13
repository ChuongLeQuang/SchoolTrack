import os
import sys
import logging
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QSplashScreen
from apps.main_app.src.views.main_window import MainWindow


def main() -> None:
    """
    EN: Main entry point for the SchoolTrack application.
    VI: Điểm neo khởi chạy chính cho ứng dụng SchoolTrack.
    """
    # Cấu hình logging cơ bản theo chuẩn AI_RULES.md
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    app = QApplication(sys.argv)
    
    # 1. Xác định đường dẫn gốc an toàn cho assets
    if getattr(sys, 'frozen', False):
        project_root = sys._MEIPASS
    else:
        project_root = os.path.dirname(os.path.abspath(__file__))
        
    logo_path = os.path.join(project_root, "assets", "2CJ1_3D.png")
    
    # 2. Khởi tạo Splash Screen nếu tìm thấy logo
    if os.path.exists(logo_path):
        pixmap = QPixmap(logo_path)
        scaled_pixmap = pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
        splash = QSplashScreen(scaled_pixmap, Qt.WindowType.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()  # Ép vẽ Splash Screen ngay lập tức
        
        window = MainWindow()
        QTimer.singleShot(3000, lambda: (splash.close(), window.show()))  # Đợi 3 giây
    else:
        window = MainWindow()
        window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()