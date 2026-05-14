from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox, QFileDialog, QApplication
from PyQt6.QtCore import Qt
import webbrowser
import sys
import os
from datetime import datetime
from apps.main_app.src.services.class_wave_metadata_service import WaveMetadataService
from apps.main_app.src.services.core_google_api_service import GoogleApiService
from apps.main_app.src.views.class_gas_config_dialog import GASConfigDialog


class ClassLinksWidget(QGroupBox):
    """
    EN: Widget for configuring and interacting with Google Form & Sheet links of a specific wave.
    VI: Widget quản lý và cấu hình các link Google Form & Sheet của Đợt.
    """
    def __init__(self, parent=None):
        super().__init__("🔗 Cấu hình Link Đăng Ký (Gắn liền với Đợt)", parent)
        self.current_year = ""
        self.current_wave = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        links_config_layout = QVBoxLayout()
        
        row1 = QHBoxLayout()
        self.txt_form_link = QLineEdit()
        self.txt_form_link.setPlaceholderText("🔗 Link Google Form")
        self.btn_open_link = QPushButton("🌐 Mở Form")
        self.btn_open_link.clicked.connect(self.open_form_link)
        row1.addWidget(self.txt_form_link)
        row1.addWidget(self.btn_open_link)
        
        row2 = QHBoxLayout()
        self.txt_sheet_link = QLineEdit()
        self.txt_sheet_link.setPlaceholderText("📊 Link Google Sheet")
        self.btn_open_sheet = QPushButton("🌐 Mở Sheet")
        self.btn_open_sheet.clicked.connect(self.open_sheet_link)
        self.btn_download_sheet = QPushButton("📥 Tải File")
        self.btn_download_sheet.clicked.connect(self.download_sheet_file)
        self.btn_save_links = QPushButton("💾 Lưu Cấu Hình Link")
        self.btn_save_links.clicked.connect(self.save_wave_links)
        
        row2.addWidget(self.txt_sheet_link)
        row2.addWidget(self.btn_open_sheet)
        row2.addWidget(self.btn_download_sheet)
        row2.addWidget(self.btn_save_links)
        
        self.btn_gas_config = QPushButton("⚙️ Cấu hình API Google Form")
        self.btn_gas_config.clicked.connect(self.open_gas_config_dialog)
        
        links_config_layout.addLayout(row1)
        links_config_layout.addLayout(row2)
        links_config_layout.addWidget(self.btn_gas_config, alignment=Qt.AlignmentFlag.AlignRight)
        self.setLayout(links_config_layout)

    def load_data(self, year: str, wave: str) -> None:
        self.current_year = year
        self.current_wave = wave
        is_all_waves = wave == "Tất cả"
        for widget in [self.txt_form_link, self.txt_sheet_link, self.btn_save_links, self.btn_open_link, self.btn_open_sheet, self.btn_download_sheet]:
            widget.setEnabled(not is_all_waves)
        if is_all_waves:
            self.txt_form_link.setText("")
            self.txt_sheet_link.setText("")
        else:
            links = WaveMetadataService.get_wave_links(year, wave)
            self.txt_form_link.setText(links.get("form_link", ""))
            self.txt_sheet_link.setText(links.get("sheet_link", ""))

    def set_links(self, form_link: str, sheet_link: str) -> None:
        self.txt_form_link.setText(form_link)
        self.txt_sheet_link.setText(sheet_link)

    def open_form_link(self) -> None:
        link = self.txt_form_link.text().strip()
        if "script.google.com" in link: return QMessageBox.warning(self, "Nhầm lẫn Link", "Đây là link API của Google Script (Nhân viên ảo), không phải link Google Form!\n\nVui lòng dán link này vào phần '⚙️ Cấu hình API' và nhấn nút '🪄 Tự động tạo Form'.")
        if link and "script" not in link: webbrowser.open("https://" + link if not link.startswith("http") else link)
        
    def open_sheet_link(self) -> None:
        link = self.txt_sheet_link.text().strip()
        if "script.google.com" in link: return QMessageBox.warning(self, "Nhầm lẫn Link", "Đây là link API của Google Script, không phải link Google Sheet!\n\nVui lòng nhấn nút '🪄 Tự động tạo Form' để phần mềm tự sinh ra link Sheet chuẩn xác.")
        if link and "script" not in link: webbrowser.open("https://" + link if not link.startswith("http") else link)

    def download_sheet_file(self) -> None:
        sheet_link = self.txt_sheet_link.text().strip()
        if not sheet_link: return QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập link Google Sheet trước khi tải!")
        save_dir = QFileDialog.getExistingDirectory(self, "Chọn thư mục để lưu file Excel")
        if not save_dir: return
        date_str = datetime.now().strftime("%Y-%m-%d")
        wave_str = self.current_wave.replace(" ", "_") if self.current_wave and self.current_wave != "Tất cả" else "Tong_hop"
        file_name = f"[{date_str}]_KetQuaDangKy_{wave_str}.xlsx"
        save_path = os.path.join(save_dir, file_name)
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            success = GoogleApiService.download_google_sheet_as_excel(sheet_link, save_path)
            QApplication.restoreOverrideCursor()
            if success:
                reply = QMessageBox.information(self, "Tải thành công", f"Đã tải file thành công!\n\nĐường dẫn: {save_path}\n\nBạn có muốn mở thư mục chứa file không?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
                if reply == QMessageBox.StandardButton.Yes:
                    if sys.platform == "win32": os.startfile(save_dir)
                    else: import subprocess; subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", save_dir])
            else: QMessageBox.critical(self, "Tải thất bại", "Không thể tải file từ Google Sheet! Vui lòng kiểm tra lại link hoặc cấp quyền truy cập.")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Lỗi", f"Có lỗi không xác định xảy ra:\n{e}")

    def save_wave_links(self) -> None:
        if self.current_year and self.current_wave:
            WaveMetadataService.save_wave_links(self.current_year, self.current_wave, self.txt_form_link.text(), self.txt_sheet_link.text())
            QMessageBox.information(self, "Thành công", "Đã lưu cấu hình link!")

    def open_gas_config_dialog(self) -> None:
        GASConfigDialog(self).exec()