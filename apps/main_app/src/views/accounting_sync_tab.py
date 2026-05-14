from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QHeaderView, QLabel, QTableWidgetItem, 
                             QMessageBox, QFileDialog, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from apps.main_app.src.services.registration_service import RegistrationService
from apps.main_app.src.services.student_service import StudentService


class AccountingSyncTab(QWidget):
    """
    EN: Tab for syncing and reconciling accounting data with Google Form registrations.
    VI: Tab đối chiếu Kế toán với kết quả đăng ký từ Google Form.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)

        sync_toolbar = QHBoxLayout()
        self.btn_start_sync = QPushButton("📂 Chọn & Đối chiếu File Kế toán")
        self.btn_start_sync.setStyleSheet("padding: 8px 20px; font-weight: bold; font-size: 15px; background-color: #8B5CF6; color: white; border: none; border-radius: 5px;")
        self.btn_start_sync.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start_sync.clicked.connect(self.start_accounting_sync)
        
        sync_toolbar.addWidget(self.btn_start_sync)
        sync_toolbar.addStretch()
        layout.addLayout(sync_toolbar)

        self.sync_results_table = QTableWidget()
        headers = ["STT", "Họ & Tên SV", "Mã SV", "Lớp Đăng Ký", "Trạng thái Xử lý", "Chi tiết"]
        self.sync_results_table.setColumnCount(len(headers))
        self.sync_results_table.setHorizontalHeaderLabels(headers)
        
        header = self.sync_results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        
        self.sync_results_table.setStyleSheet("font-size: 13px;")
        self.sync_results_table.setAlternatingRowColors(True)
        layout.addWidget(self.sync_results_table)

        self.lbl_sync_stats = QLabel("Trạng thái: Sẵn sàng để đối chiếu.")
        self.lbl_sync_stats.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_sync_stats)

    def start_accounting_sync(self) -> None:
        """
        EN: Start the accounting sync process by selecting Form and Accounting files.
        VI: Bắt đầu quy trình đối chiếu file Kế toán và file Google Form.
        """
        QMessageBox.information(self, "Bước 1/2", "Đầu tiên, vui lòng chọn file KẾT QUẢ ĐĂNG KÝ (tải từ Google Form).")
        form_file, _ = QFileDialog.getOpenFileName(self, "Chọn file Đăng ký", "", "Excel Files (*.xlsx *.xls)")
        if not form_file: return
        
        QMessageBox.information(self, "Bước 2/2", "Tiếp theo, vui lòng chọn file KẾ TOÁN (Danh sách chuyển khoản).")
        acc_file, _ = QFileDialog.getOpenFileName(self, "Chọn file Kế toán", "", "Excel Files (*.xlsx *.xls)")
        if not acc_file: return
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            students_db = StudentService.get_students_from_excel(StudentService.get_file_path())
            results, stats = RegistrationService.sync_accounting_with_form(form_file, acc_file, students_db)
            
            self.sync_results_table.setUpdatesEnabled(False)
            self.sync_results_table.setRowCount(0)
            self.sync_results_table.setRowCount(len(results))
            for i, res in enumerate(results):
                self.sync_results_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                self.sync_results_table.setItem(i, 1, QTableWidgetItem(res["student_name"]))
                self.sync_results_table.setItem(i, 2, QTableWidgetItem(res["student_id"]))
                self.sync_results_table.setItem(i, 3, QTableWidgetItem(res["class_code"]))
                
                item_status = QTableWidgetItem(res["status"])
                font = item_status.font()
                font.setBold(True)
                item_status.setFont(font)
                if res["status"] == "Hợp lệ": item_status.setForeground(QColor("#16A34A"))
                elif "Lệch" in res["status"]: item_status.setForeground(QColor("#D97706"))
                else: item_status.setForeground(QColor("#DC2626"))
                self.sync_results_table.setItem(i, 4, item_status)
                self.sync_results_table.setItem(i, 5, QTableWidgetItem(res["detail"]))
                
            self.sync_results_table.setUpdatesEnabled(True)
            self.lbl_sync_stats.setText(f"Thống kê: {stats['hop_le']} Hợp lệ | {stats['lech_khop']} Lệch khớp | {stats['chua_dong']} Chưa đóng tiền")
            QApplication.restoreOverrideCursor()
            QMessageBox.information(self, "Hoàn tất", f"Đã đối chiếu xong!\n\n- Hợp lệ: {stats['hop_le']}\n- Lệch khớp: {stats['lech_khop']}\n- Chưa đóng tiền: {stats['chua_dong']}")
        except Exception as e:
            # EN: Catch unexpected errors during file processing
            # VI: Bắt lỗi không lường trước khi xử lý file
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra khi xử lý file:\n{e}")
        finally:
            QApplication.restoreOverrideCursor()