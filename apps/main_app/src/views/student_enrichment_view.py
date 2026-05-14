import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QLabel, QHeaderView, 
                             QTableWidgetItem, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from apps.main_app.src.services.student_service import StudentService

class StudentEnrichmentView(QWidget):
    """
    EN: View for Data Enrichment (scanning and reviewing form updates).
    VI: Màn hình Làm giàu Dữ liệu (quét và duyệt thông tin mới từ Form).
    """
    def __init__(self) -> None:
        super().__init__()
        self.updates_file = StudentService.get_pending_updates_file()
        self.updates_data = []
        self._setup_ui()
        self.load_data()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        lbl_title = QLabel("✨ Trạm Làm Giàu Dữ Liệu Sinh Viên")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2563EB;")
        layout.addWidget(lbl_title)
        
        lbl_info = QLabel("Chọn file Excel tải về từ Google Form. Hệ thống sẽ tự động đối chiếu để phát hiện SĐT, Email mới hoặc Đề xuất sửa Tên.\nSau đó bạn có thể Duyệt để cập nhật thẳng vào CSDL gốc.")
        lbl_info.setStyleSheet("color: #4B5563; font-style: italic; font-size: 14px;")
        layout.addWidget(lbl_info)
        
        toolbar = QHBoxLayout()
        self.btn_scan = QPushButton("📂 Chọn File Form để Quét")
        self.btn_scan.setStyleSheet("padding: 8px 15px; font-weight: bold; font-size: 14px; background-color: #8B5CF6; color: white; border: none; border-radius: 5px;")
        self.btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_scan.clicked.connect(self.scan_file)
        
        self.btn_reload = QPushButton("🔄 Tải lại Danh sách")
        self.btn_reload.setStyleSheet("padding: 8px 15px; font-weight: bold; font-size: 14px;")
        self.btn_reload.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reload.clicked.connect(self.load_data)
        
        toolbar.addWidget(self.btn_scan)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_reload)
        layout.addLayout(toolbar)
        
        self.table = QTableWidget()
        headers = ["MSV", "Loại", "Thông tin Cũ", "Thông tin Mới", "Hành động"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setStyleSheet("font-size: 14px;")
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self.lbl_stats = QLabel("Đang chờ duyệt: 0 mục")
        self.lbl_stats.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.lbl_stats)

    def scan_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file Excel từ Google Form", "", "Excel Files (*.xlsx *.xls)"
        )
        if not file_path: return
        
        try:
            students = StudentService.get_students_from_excel(StudentService.get_file_path())
            count = StudentService.scan_form_for_enrichment(file_path, students)
            if count > 0:
                QMessageBox.information(self, "Thành công", f"Đã quét và phát hiện {count} thông tin mới/đề xuất sửa!")
                self.load_data()
            else:
                QMessageBox.information(self, "Hoàn tất", "Không phát hiện thông tin nào mới hoặc sai lệch cần cập nhật.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra khi quét file:\n{e}")

    def load_data(self) -> None:
        self.updates_data = []
        if os.path.exists(self.updates_file):
            try:
                with open(self.updates_file, "r", encoding="utf-8") as f: self.updates_data = json.load(f)
            except Exception: pass
                
        self.table.setUpdatesEnabled(False)
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.updates_data))
        for idx, item in enumerate(self.updates_data):
            self.table.setItem(idx, 0, QTableWidgetItem(item.get("msv", "")))
            type_item = QTableWidgetItem(item.get("type", ""))
            font = type_item.font()
            font.setBold(True)
            type_item.setFont(font)
            type_item.setForeground(QColor("#F59E0B") if item.get("type") == "Tên" else QColor("#3B82F6"))
            self.table.setItem(idx, 1, type_item)
            self.table.setItem(idx, 2, QTableWidgetItem(item.get("old_val", "")))
            self.table.setItem(idx, 3, QTableWidgetItem(item.get("new_val", "")))
            
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(5)
            
            btn_approve = QPushButton("✅ Duyệt")
            btn_approve.setStyleSheet("background-color: #10B981; color: white; border: none; border-radius: 3px; padding: 4px;")
            btn_approve.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_approve.clicked.connect(lambda checked, r=idx: self.approve_update(r))
            
            btn_reject = QPushButton("❌ Bỏ qua")
            btn_reject.setStyleSheet("background-color: #EF4444; color: white; border: none; border-radius: 3px; padding: 4px;")
            btn_reject.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_reject.clicked.connect(lambda checked, r=idx: self._remove_from_list(r))
            
            action_layout.addWidget(btn_approve)
            action_layout.addWidget(btn_reject)
            self.table.setCellWidget(idx, 4, action_widget)
            
        self.table.setUpdatesEnabled(True)
        self.lbl_stats.setText(f"Đang chờ duyệt: {len(self.updates_data)} mục")

    def _remove_from_list(self, row_idx: int) -> None:
        self.updates_data.pop(row_idx)
        with open(self.updates_file, "w", encoding="utf-8") as f: json.dump(self.updates_data, f, indent=4, ensure_ascii=False)
        self.load_data()

    def approve_update(self, row_idx: int) -> None:
        item = self.updates_data[row_idx]
        try:
            students = StudentService.get_students_from_excel(StudentService.get_file_path())
            target = next((s for s in students if s.student_id == item["msv"]), None)
            if target:
                if item["type"] == "Tên": target.full_name = item["new_val"]
                elif item["type"] == "SĐT":
                    old = [p.strip() for p in str(target.phone_number).split(",") if p.strip()]
                    if item["new_val"] not in old: old.insert(0, item["new_val"]); target.phone_number = ", ".join(old)
                elif item["type"] == "Email":
                    old = [e.strip() for e in str(target.email).split(",") if e.strip()]
                    if item["new_val"] not in old: old.insert(0, item["new_val"]); target.email = ", ".join(old)
                StudentService.save_student_to_excel(StudentService.get_file_path(), target)
                self._remove_from_list(row_idx)
            else: QMessageBox.warning(self, "Lỗi", "Không tìm thấy sinh viên trong CSDL gốc!")
        except Exception as e: QMessageBox.critical(self, "Lỗi", f"Có lỗi xảy ra:\n{e}")