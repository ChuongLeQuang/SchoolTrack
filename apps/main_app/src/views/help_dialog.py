from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PyQt6.QtCore import Qt


class HelpDialog(QDialog):
    """
    EN: A dialog to display help content (HTML formatted).
    VI: Hộp thoại hiển thị nội dung hướng dẫn (định dạng HTML).
    """
    def __init__(self, html_content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📖 Hướng Dẫn Sử Dụng SchoolTrack")
        self.setMinimumSize(800, 600)

        # Thêm các nút Minimize và Maximize vào thanh tiêu đề
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint)

        layout = QVBoxLayout(self)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setHtml(html_content)
        layout.addWidget(self.text_browser)

        self.close_button = QPushButton("Đóng")
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignRight)