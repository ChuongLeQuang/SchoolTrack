from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QComboBox, QPushButton, QDateEdit, QLabel, QMessageBox)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QIcon, QPixmap
from apps.main_app.src.models.entities import Student


class StudentDialog(QDialog):
    """
    EN: Dialog for adding or editing a Student.
    VI: Hộp thoại để thêm hoặc sửa thông tin Sinh viên.
    """
    def __init__(self, parent=None, student: Student = None, new_id: str = None):
        super().__init__(parent)
        self.student = student
        self.is_edit_mode = student is not None
        self.new_id = new_id
        
        self.setWindowTitle("✏️ Sửa Thông tin Sinh viên" if self.is_edit_mode else "➕ Thêm Sinh viên Mới")
        
        # Loại bỏ nút "?" (Help) mặc định trên thanh tiêu đề của Dialog
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # Xóa bỏ icon cửa sổ mặc định của Windows bằng một icon trong suốt
        transparent_pixmap = QPixmap(1, 1)
        transparent_pixmap.fill(Qt.GlobalColor.transparent)
        self.setWindowIcon(QIcon(transparent_pixmap))
        
        self.resize(400, 350)
        self._setup_ui()
        
        if self.is_edit_mode:
            self._load_data()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.txt_id = QLineEdit()
        if self.is_edit_mode:
            self.txt_id.setReadOnly(True)  # Không cho sửa MSV nếu đang Sửa
            self.txt_id.setStyleSheet("background-color: #F3F4F6; color: #6B7280;")
            self.txt_id.setToolTip("Mã Sinh viên là thông tin định danh (Khóa chính), không thể thay đổi.")
        elif getattr(self, 'new_id', None):
            self.txt_id.setText(self.new_id)

        self.txt_name = QLineEdit()
        
        self.date_dob = QDateEdit()
        self.date_dob.setDisplayFormat("dd/MM/yyyy")
        self.date_dob.setCalendarPopup(True)
        self.date_dob.setDate(QDate.currentDate())
        
        self.txt_email = QLineEdit()
        self.txt_phone = QLineEdit()
        
        self.cb_status = QComboBox()
        self.cb_status.addItems(["Đang học", "Tạm nghỉ", "Nghỉ học", "Tốt nghiệp", "Khác"])
        
        self.txt_balance = QLineEdit()
        self.txt_balance.setPlaceholderText("Ví dụ: 5000000")

        form_layout.addRow("Mã Sinh viên (*):", self.txt_id)
        form_layout.addRow("Họ và tên (*):", self.txt_name)
        form_layout.addRow("Ngày sinh:", self.date_dob)
        form_layout.addRow("Email:", self.txt_email)
        form_layout.addRow("Số điện thoại:", self.txt_phone)
        form_layout.addRow("Trạng thái:", self.cb_status)
        form_layout.addRow("Số dư học phí:", self.txt_balance)

        layout.addLayout(form_layout)

        # Required fields note
        lbl_required = QLabel("(*) Thông tin bắt buộc nhập")
        lbl_required.setStyleSheet("color: #DC2626; font-style: italic; font-size: 12px;")
        layout.addWidget(lbl_required)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("💾 Lưu")
        self.btn_save.setStyleSheet("background-color: #3B82F6; color: white; padding: 6px 15px; font-weight: bold; border-radius: 4px;")
        self.btn_cancel = QPushButton("❌ Hủy")
        self.btn_cancel.setStyleSheet("background-color: #EF4444; color: white; padding: 6px 15px; font-weight: bold; border-radius: 4px;")
        
        self.btn_save.clicked.connect(self.validate_and_accept)
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_data(self) -> None:
        self.txt_id.setText(self.student.student_id)
        self.txt_name.setText(self.student.full_name)
        if self.student.date_of_birth:
            self.date_dob.setDate(QDate(self.student.date_of_birth.year, self.student.date_of_birth.month, self.student.date_of_birth.day))
        self.txt_email.setText(self.student.email)
        self.txt_phone.setText(self.student.phone_number)
        self.cb_status.setCurrentText(self.student.study_status)
        self.txt_balance.setText(str(self.student.tuition_balance))

    def validate_and_accept(self) -> None:
        """
        EN: Validate required fields before accepting.
        VI: Kiểm tra các trường bắt buộc trước khi lưu.
        """
        if not self.txt_id.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Mã Sinh viên!")
            self.txt_id.setFocus()
            return
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Họ và tên!")
            self.txt_name.setFocus()
            return
        self.accept()

    def get_student_data(self) -> dict:
        """
        EN: Get data entered in the form.
        VI: Lấy dữ liệu được nhập trên form.
        """
        balance_str = self.txt_balance.text().strip().replace(",", "").replace(".", "")
        return {
            "student_id": self.txt_id.text().strip(),
            "full_name": self.txt_name.text().strip(),
            "date_of_birth": self.date_dob.date().toPyDate(),
            "email": self.txt_email.text().strip(),
            "phone_number": self.txt_phone.text().strip(),
            "study_status": self.cb_status.currentText(),
            "tuition_balance": int(balance_str) if balance_str.lstrip('-').isdigit() else 0
        }