from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QComboBox, QPushButton, 
                             QTableWidget, QLabel, QHeaderView, QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPixmap
import os
import sys
import logging
from datetime import datetime
from apps.main_app.src.services.student_service import StudentService
from apps.main_app.src.models.entities import Student
from apps.main_app.src.views.student_dialog import StudentDialog


class StudentView(QWidget):
    """
    EN: Student Management UI containing data table and toolbars.
    VI: Giao diện quản lý Sinh viên chứa bảng dữ liệu và thanh công cụ.
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.is_data_loaded = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. Header / Toolbar (Khu vực công cụ tìm kiếm và lọc)
        toolbar_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm theo MSV, Họ, Tên...")
        self.search_input.setFixedWidth(300)
        self.search_input.setStyleSheet("padding: 6px; font-size: 14px;")

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Tất cả trạng thái", "Đang học", "Tạm nghỉ", "Nghỉ học", "Tốt nghiệp", "Khác"])
        self.status_filter.setStyleSheet("padding: 6px; font-size: 14px;")

        self.btn_reload = QPushButton("🔄 Tải lại Dữ liệu")
        self.btn_reload.setStyleSheet("padding: 6px 15px; font-weight: bold; font-size: 14px;")
        self.btn_reload.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reload.clicked.connect(self.load_data)

        self.btn_add = QPushButton("➕ Thêm")
        self.btn_add.setStyleSheet("padding: 6px 15px; font-weight: bold; font-size: 14px; background-color: #3B82F6; color: white; border: none; border-radius: 5px;")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.clicked.connect(self.open_add_dialog)

        self.btn_edit = QPushButton("✏️ Sửa")
        self.btn_edit.setStyleSheet("padding: 6px 15px; font-weight: bold; font-size: 14px; background-color: #F59E0B; color: white; border: none; border-radius: 5px;")
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.clicked.connect(self.open_edit_dialog)

        self.btn_delete = QPushButton("🗑️ Xóa")
        self.btn_delete.setStyleSheet("padding: 6px 15px; font-weight: bold; font-size: 14px; background-color: #EF4444; color: white; border: none; border-radius: 5px;")
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self.delete_student)

        # Kết nối sự kiện gõ chữ và chọn combo box với hàm lọc
        self.search_input.textChanged.connect(self.filter_table)
        self.status_filter.currentTextChanged.connect(self.filter_table)

        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addWidget(self.status_filter)
        toolbar_layout.addStretch()  # Đẩy nút tải lại sang góc phải
        toolbar_layout.addWidget(self.btn_add)
        toolbar_layout.addWidget(self.btn_edit)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addWidget(self.btn_reload)

        layout.addLayout(toolbar_layout)

        # 2. Data Table (Khu vực Bảng dữ liệu)
        self.table = QTableWidget()
        headers = ["Mã SV", "Họ và tên", "Ngày sinh", "Email", "Số điện thoại", "Lớp đang học", "Số dư học phí", "Trạng thái"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        # Căn chỉnh độ rộng các cột
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Mã SV
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Họ và tên
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Ngày sinh
        
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)       # Email
        self.table.setColumnWidth(3, 180)                                        # Độ rộng mặc định cho Email
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Số điện thoại
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)           # Lớp đang học
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Số dư học phí
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Trạng thái
        
        self.table.setStyleSheet("font-size: 13px;")
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self.open_edit_dialog)
        layout.addWidget(self.table)

        # 3. Footer / Stats (Khu vực thống kê dưới cùng)
        self.lbl_stats = QLabel("Tổng số: 0 sinh viên")
        self.lbl_stats.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl_stats)

        self.setLayout(layout)

    def load_data(self) -> None:
        """
        EN: Load student data from Excel and populate the table.
        VI: Đọc dữ liệu sinh viên từ file Excel và điền vào bảng.
        """
        logging.info("⏳ Đang tiến hành đọc file Excel, vui lòng đợi...")
        
        # Sử dụng đường dẫn tuyệt đối để đảm bảo luôn tìm thấy file
        file_path = StudentService.get_file_path()
        logging.info(f"📂 Đang tìm file tại: {file_path}")
        
        try:
            students = StudentService.get_students_from_excel(file_path)
            self.table.setRowCount(len(students))
            
            for row_idx, student in enumerate(students):
                self.table.setItem(row_idx, 0, QTableWidgetItem(student.student_id))
                self.table.setItem(row_idx, 1, QTableWidgetItem(student.full_name))
                
                dob_str = student.date_of_birth.strftime("%d/%m/%Y") if student.date_of_birth else ""
                self.table.setItem(row_idx, 2, QTableWidgetItem(dob_str))
                
                self.table.setItem(row_idx, 3, QTableWidgetItem(student.email))
                self.table.setItem(row_idx, 4, QTableWidgetItem(student.phone_number))
                
                # Tạm thời để trống cột "Lớp đang học"
                self.table.setItem(row_idx, 5, QTableWidgetItem(""))
                
                # Format Số dư học phí: 5,000,000
                balance_str = f"{student.tuition_balance:,}"
                item_balance = QTableWidgetItem(balance_str)
                item_balance.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.table.setItem(row_idx, 6, item_balance)
                
                item_status = QTableWidgetItem(student.study_status)
                font = item_status.font()
                font.setBold(True)
                item_status.setFont(font)
                
                status_lower = student.study_status.lower()
                if status_lower == "đang học":
                    item_status.setForeground(QColor("#16A34A"))  # Xanh lá
                elif status_lower in ["nghỉ học", "tạm nghỉ"]:
                    item_status.setForeground(QColor("#DC2626"))  # Đỏ
                elif status_lower == "tốt nghiệp":
                    item_status.setForeground(QColor("#2563EB"))  # Xanh dương
                    
                self.table.setItem(row_idx, 7, item_status)
                
            # Thống kê chi tiết số lượng theo trạng thái
            dang_hoc = sum(1 for s in students if s.study_status.lower() == "đang học")
            tam_nghi = sum(1 for s in students if s.study_status.lower() == "tạm nghỉ")
            nghi_hoc = sum(1 for s in students if s.study_status.lower() == "nghỉ học")
            self.lbl_stats.setText(f"Tổng số: {len(students)} sinh viên (đang học: {dang_hoc} | tạm nghỉ: {tam_nghi} | nghỉ học: {nghi_hoc})")
            self.is_data_loaded = True
        except Exception as e:
            logging.error(f"[LỖI TẢI DỮ LIỆU]: {e}")
            QMessageBox.warning(self, "Lỗi tải dữ liệu", f"Không thể tải dữ liệu từ Excel:\n{e}")

    def filter_table(self) -> None:
        """
        EN: Filter the table based on search text and status selection.
        VI: Lọc dữ liệu bảng dựa trên từ khóa tìm kiếm và trạng thái.
        """
        search_text = self.search_input.text().lower().strip()
        status_text = self.status_filter.currentText()

        for row in range(self.table.rowCount()):
            item_id = self.table.item(row, 0)
            item_name = self.table.item(row, 1)
            item_status = self.table.item(row, 7)

            if not item_id or not item_name or not item_status:
                continue

            # Lọc theo text (tìm trong cả MSV và Họ Tên)
            match_search = search_text in item_id.text().lower() or search_text in item_name.text().lower()
            # Lọc theo trạng thái
            match_status = True if status_text == "Tất cả trạng thái" else item_status.text() == status_text

            # Ẩn dòng nếu không khớp cả 2 điều kiện
            self.table.setRowHidden(row, not (match_search and match_status))

    def generate_new_student_id(self) -> str:
        """
        EN: Generate a new student ID based on existing records.
        VI: Tạo mã sinh viên mới dựa trên các mã đã có (VD: SV001).
        """
        max_id = 0
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                text_id = item.text().strip()
                digits = ''.join(filter(str.isdigit, text_id))
                if digits:
                    max_id = max(max_id, int(digits))
        return f"SV{(max_id + 1):03d}"

    def open_add_dialog(self) -> None:
        """
        EN: Open dialog to add a new student.
        VI: Mở hộp thoại thêm sinh viên mới.
        """
        new_id = self.generate_new_student_id()
        dialog = StudentDialog(self, new_id=new_id)
        if dialog.exec():
            data = dialog.get_student_data()
            
            # Kiểm tra trùng mã sinh viên khi THÊM MỚI
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item and item.text().strip().lower() == data["student_id"].lower():
                    QMessageBox.warning(self, "Lỗi", f"Mã Sinh viên '{data['student_id']}' đã tồn tại trong danh sách!")
                    return
                    
            try:
                file_path = StudentService.get_file_path()
                student = Student(**data)
                
                StudentService.save_student_to_excel(file_path, student)
                QMessageBox.information(self, "Thành công", f"Đã thêm mới sinh viên:\n{student.student_id} - {student.full_name}")
                QTimer.singleShot(50, self.load_data)
            except PermissionError:
                QMessageBox.warning(self, "Lỗi truy cập", "File Excel đang được mở.\nVui lòng đóng file Excel trước khi lưu!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể lưu dữ liệu:\n{e}")

    def delete_student(self) -> None:
        """
        EN: Delete the selected student after confirmation.
        VI: Xóa sinh viên đang chọn sau khi xác nhận.
        """
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một sinh viên để xóa!")
            return
            
        item_id = self.table.item(current_row, 0)
        item_name = self.table.item(current_row, 1)
        
        if not item_id or not item_name:
            return
            
        student_id = item_id.text()
        student_name = item_name.text()
        
        reply = QMessageBox.question(
            self, 
            "Xác nhận xóa", 
            f"Bạn có chắc chắn muốn xóa sinh viên:\n{student_id} - {student_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            file_path = StudentService.get_file_path()
            try:
                if StudentService.delete_student_from_excel(file_path, student_id):
                    QMessageBox.information(self, "Thành công", f"Đã xóa sinh viên {student_id} thành công!")
                    QTimer.singleShot(50, self.load_data)
                else:
                    QMessageBox.warning(self, "Lỗi", f"Không tìm thấy mã sinh viên {student_id} để xóa.")
            except PermissionError:
                QMessageBox.warning(self, "Lỗi truy cập", "File Excel đang được mở.\nVui lòng đóng file Excel trước khi xóa!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Có lỗi xảy ra khi xóa sinh viên:\n{e}")

    def open_edit_dialog(self, item=None) -> None:
        """
        EN: Open the dialog to edit the selected student.
        VI: Mở hộp thoại sửa thông tin sinh viên đang được chọn.
        """
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một sinh viên để sửa!")
            return
            
        def get_item_text(col: int) -> str:
            it = self.table.item(current_row, col)
            return it.text() if it else ""

        # Khôi phục dữ liệu từ dòng hiện tại trên bảng
        student_id = get_item_text(0)
        full_name = get_item_text(1)
        dob_str = get_item_text(2)
        
        dob = None
        if dob_str:
            try: dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
            except ValueError: pass
                
        email = get_item_text(3)
        phone = get_item_text(4)
        balance_str = get_item_text(6).replace(",", "")
        status = get_item_text(7)

        student = Student(
            student_id=student_id,
            full_name=full_name,
            date_of_birth=dob,
            email=email,
            phone_number=phone,
            study_status=status,
            tuition_balance=int(balance_str) if balance_str.lstrip('-').isdigit() else 0
        )
        
        dialog = StudentDialog(self, student=student)
        if dialog.exec():
            data = dialog.get_student_data()
            try:
                file_path = StudentService.get_file_path()
                student = Student(**data)
                
                StudentService.save_student_to_excel(file_path, student)
                QMessageBox.information(self, "Thành công", f"Đã cập nhật sinh viên:\n{student.student_id} - {student.full_name}")
                QTimer.singleShot(50, self.load_data)
            except PermissionError:
                QMessageBox.warning(self, "Lỗi truy cập", "File Excel đang được mở.\nVui lòng đóng file Excel trước khi lưu!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể lưu dữ liệu:\n{e}")