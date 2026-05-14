from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QLabel, QDialogButtonBox
from PyQt6.QtCore import QSettings


class GASConfigDialog(QDialog):
    """
    EN: Dialog for configuring Google Apps Script API connection parameters.
    VI: Hộp thoại cấu hình thông số kết nối Google Apps Script tự động.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cấu hình API Google Form tự động")
        self.setMinimumWidth(550)
        self.settings = QSettings("SchoolTrackOrg", "SchoolTrack")
        
        layout = QFormLayout(self)
        
        self.txt_url = QLineEdit()
        self.txt_url.setPlaceholderText("https://script.google.com/macros/s/.../exec")
        self.txt_url.setText(self.settings.value("gas/web_app_url", ""))
        
        self.txt_template = QLineEdit()
        self.txt_template.setPlaceholderText("ID của file Google Form mẫu (Ví dụ: 1BxiMVs...)")
        self.txt_template.setText(self.settings.value("gas/template_id", ""))
        
        self.txt_secret = QLineEdit()
        self.txt_secret.setPlaceholderText("Mật khẩu bảo mật (Ví dụ: mat_khau_123)")
        self.txt_secret.setText(self.settings.value("gas/secret", "schooltrack_secret_123"))
        
        layout.addRow("Web App URL:", self.txt_url)
        layout.addRow("Form Mẫu ID:", self.txt_template)
        layout.addRow("Secret Token:", self.txt_secret)
        
        lbl_hint = QLabel("💡 Lưu ý: Bạn phải thiết lập Web App trên Google Drive và dán URL vào đây trước khi sử dụng.")
        lbl_hint.setWordWrap(True)
        lbl_hint.setStyleSheet("color: #6B7280; font-style: italic; margin-top: 10px;")
        layout.addRow(lbl_hint)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)
        
    def accept(self):
        self.settings.setValue("gas/web_app_url", self.txt_url.text().strip())
        self.settings.setValue("gas/template_id", self.txt_template.text().strip())
        self.settings.setValue("gas/secret", self.txt_secret.text().strip())
        super().accept()