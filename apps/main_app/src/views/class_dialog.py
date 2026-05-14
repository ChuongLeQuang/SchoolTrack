from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLineEdit, QComboBox, QPushButton, QDateEdit, QLabel, QMessageBox, QSpinBox)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QIcon, QPixmap
from apps.main_app.src.models.entities import ClassInfo
from apps.main_app.src.services.core_config_service import ConfigService


class ClassDialog(QDialog):
    """
    EN: Dialog for adding a planned class or editing an existing one.
    VI: Hộp thoại để thêm mới lớp dự kiến hoặc sửa thông tin lớp.
    """
    def __init__(self, parent=None, class_info: ClassInfo = None, existing_codes: list = None):
        super().__init__(parent)
        self.class_info = class_info
        self.is_edit_mode = class_info is not None
        self.existing_codes = existing_codes or []
        
        self.templates = ConfigService.get_class_templates()
        
        self.setWindowTitle("✏️ Sửa Lớp học" if self.is_edit_mode else "➕ Thêm Lớp Dự kiến Mới")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        transparent_pixmap = QPixmap(1, 1)
        transparent_pixmap.fill(Qt.GlobalColor.transparent)
        self.setWindowIcon(QIcon(transparent_pixmap))
        
        self.resize(450, 400)
        self._setup_ui()
        
        if self.is_edit_mode:
            self._load_data()
        else:
            self._update_generated_code()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        
        self.lbl_warning = QLabel()
        self.lbl_warning.setStyleSheet("color: #D97706; font-style: italic; font-weight: bold; font-size: 13px; margin-bottom: 5px;")
        self.lbl_warning.setWordWrap(True)
        self.lbl_warning.setVisible(False)
        layout.addWidget(self.lbl_warning)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Template selection (Chỉ hiển thị khi thêm mới)
        self.cb_template = QComboBox()
        self.cb_template.addItem("--- Chọn Mẫu Lớp ---", None)
        for code, data in self.templates.items():
            self.cb_template.addItem(f"{code} - {data['name']}", code)
        self.cb_template.currentIndexChanged.connect(self._on_template_changed)
        
        if not self.is_edit_mode:
            form_layout.addRow("Chọn Cấp độ (*):", self.cb_template)

        self.txt_code = QLineEdit()
        self.txt_code.setReadOnly(True)
        self.txt_code.setStyleSheet("background-color: #F3F4F6; color: #1D4ED8; font-weight: bold; font-size: 14px;")
        
        self.txt_name = QLineEdit()
        
        self.cb_location = QComboBox()
        self.cb_location.setEditable(True)
        self.cb_location.addItems(ConfigService.get_locations())
        
        self.txt_room = QLineEdit()
        # Khóa ô Phòng học nếu là tạo mới hoặc đang sửa lớp dự kiến (10 ký tự)
        if not self.is_edit_mode or (self.class_info and len(self.class_info.class_code) == 10):
            self.txt_room.setPlaceholderText("Sẽ được cấp khi chốt lớp")
            self.txt_room.setEnabled(False)
            self.txt_room.setStyleSheet("background-color: #F3F4F6; color: #9CA3AF;")
        
        self.cb_session = QComboBox()
        self.cb_session.addItems(ConfigService.get_sessions())
        # Buổi học cố định, không editable
        self.cb_session.currentTextChanged.connect(self._on_session_changed)
        
        self.cb_schedule = QComboBox()
        self.cb_schedule.setEditable(True)
        self.cb_schedule.addItems(ConfigService.get_schedules())
        
        self.cb_time_slot = QComboBox()
        self.cb_time_slot.setEditable(True)
        self.cb_time_slot.addItems(ConfigService.get_time_slots())
        
        self.date_start = QDateEdit()
        self.date_start.setDisplayFormat("MM/yyyy")
        self.date_start.setDate(QDate.currentDate())
        self.date_start.dateChanged.connect(self._update_generated_code)
        
        self.date_end = QDateEdit()
        self.date_end.setDisplayFormat("dd/MM/yyyy")
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate().addMonths(3))
        
        self.sb_min = QSpinBox()
        self.sb_min.setRange(0, 100)
        
        self.sb_max = QSpinBox()
        self.sb_max.setRange(1, 100)

        form_layout.addRow("Mã Lớp (Tự sinh):", self.txt_code)
        form_layout.addRow("Tên Lớp (*):", self.txt_name)
        form_layout.addRow("Tháng Khai giảng:", self.date_start)
        form_layout.addRow("Ngày Kết thúc:", self.date_end)
        form_layout.addRow("Địa điểm (*):", self.cb_location)
        form_layout.addRow("Phòng học:", self.txt_room)
        form_layout.addRow("Buổi học (*):", self.cb_session)
        form_layout.addRow("Lịch học (*):", self.cb_schedule)
        form_layout.addRow("Giờ học (*):", self.cb_time_slot)
        form_layout.addRow("Số lượng Min:", self.sb_min)
        form_layout.addRow("Số lượng Max:", self.sb_max)

        layout.addLayout(form_layout)

        lbl_required = QLabel("(*) Thông tin bắt buộc nhập")
        lbl_required.setStyleSheet("color: #DC2626; font-style: italic; font-size: 12px;")
        layout.addWidget(lbl_required)

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

    def _on_session_changed(self, session: str) -> None:
        """
        EN: Auto-suggest time slot when session changes.
        VI: Tự động gợi ý giờ học phù hợp khi thay đổi Buổi học.
        """
        session_lower = session.lower()
        
        def get_start_hour(ts: str) -> int:
            try:
                return int(ts.split(":")[0].strip())
            except Exception:
                return -1
                
        suggested_slot = None
        for i in range(self.cb_time_slot.count()):
            ts = self.cb_time_slot.itemText(i)
            h = get_start_hour(ts)
            if h == -1: continue
            
            if "sáng" in session_lower and 4 <= h < 12: suggested_slot = ts; break
            elif "chiều" in session_lower and 12 <= h < 18: suggested_slot = ts; break
            elif "tối" in session_lower and 18 <= h <= 23: suggested_slot = ts; break
                
        if suggested_slot:
            self.cb_time_slot.setCurrentText(suggested_slot)
        else:
            # Fallback nếu không có giờ nào khớp
            if "sáng" in session_lower: self.cb_time_slot.setCurrentText("08:00 - 10:00")
            elif "chiều" in session_lower: self.cb_time_slot.setCurrentText("14:00 - 16:00")
            elif "tối" in session_lower: self.cb_time_slot.setCurrentText("18:00 - 20:00")

    def _on_template_changed(self, index: int = 0) -> None:
        """Tự động điền thông tin dựa trên mẫu lớp (Level) được chọn."""
        level_code = self.cb_template.currentData()
        if level_code and level_code in self.templates:
            tpl = self.templates[level_code]
            self.txt_name.setText(tpl.get("name", ""))
            self.cb_location.setCurrentText(tpl.get("location", ""))
            self.cb_session.setCurrentText(tpl.get("session", "Tối"))
            self.cb_schedule.setCurrentText(tpl.get("schedule", "2-4-6"))
            self.cb_time_slot.setCurrentText(tpl.get("time_slot", "18:00 - 20:00"))
            self.sb_min.setValue(tpl.get("min", 15))
            self.sb_max.setValue(tpl.get("max", 30))
        self._update_generated_code()

    def _update_generated_code(self, qdate=None) -> None:
        """Logic tự sinh Mã 10 ký tự: LNH + MM + YY + Level + Hậu tố (A, B, C...)"""
        if self.is_edit_mode:
            return
            
        level_code = self.cb_template.currentData()
        if not level_code:
            self.txt_code.setText("Vui lòng chọn Cấp độ...")
            return
            
        dt = self.date_start.date()
        month = f"{dt.month():02d}"
        year_short = str(dt.year())[-2:]
        
        base_code = f"LNH{month}{year_short}{level_code}"
        suffix = "A"
        
        if self.existing_codes:
            # Lọc các mã trùng base_code và có đúng 10 ký tự
            matching_codes = [code for code in self.existing_codes if code.startswith(base_code) and len(code) == 10]
            if matching_codes:
                last_chars = [code[-1] for code in matching_codes if code[-1].isalpha()]
                if last_chars:
                    highest_char = max(last_chars).upper()
                    if highest_char < 'Z':
                        suffix = chr(ord(highest_char) + 1)
                        
        generated_code = f"{base_code}{suffix}"
        self.txt_code.setText(generated_code)

    def _load_data(self) -> None:
        self.txt_code.setText(self.class_info.class_code)
        self.txt_name.setText(self.class_info.class_name)
        self.cb_location.setCurrentText(self.class_info.location)
        room_val = getattr(self.class_info, 'room', '')
        self.txt_room.setText("" if str(room_val).lower() == "none" else room_val)
        self.cb_session.setCurrentText(self.class_info.session)
        self.cb_schedule.setCurrentText(self.class_info.schedule)
        self.cb_time_slot.setCurrentText(self.class_info.time_slot)
        self.sb_min.setValue(self.class_info.min_students)
        self.sb_max.setValue(self.class_info.max_students)
        
        try:
            parts = self.class_info.start_month_year.split("/")
            if len(parts) == 2:
                self.date_start.setDate(QDate(int(parts[1]), int(parts[0]), 1))
        except Exception:
            pass
            
        if self.class_info.end_date:
            self.date_end.setDate(QDate(self.class_info.end_date.year, self.class_info.end_date.month, self.class_info.end_date.day))
            
        if self.class_info.current_students > 0:
            self.lbl_warning.setText(f"🔒 BẢO VỆ DỮ LIỆU: Lớp đã có {self.class_info.current_students} SV đăng ký. Các thông tin hiển thị trên Google Form đã bị khóa cứng để tránh sai lệch.")
            self.lbl_warning.setVisible(True)
            self.txt_name.setEnabled(False)
            self.cb_location.setEnabled(False)
            self.cb_session.setEnabled(False)
            self.cb_schedule.setEnabled(False)
            self.cb_time_slot.setEnabled(False)
        else:
            self.lbl_warning.setText("⚠️ LƯU Ý: Nếu lớp này đã được copy lên Google Form, hãy nhớ cập nhật lại trên Form nếu bạn sửa đổi thông tin tại đây!")
            self.lbl_warning.setVisible(True)

    def validate_and_accept(self) -> None:
        if not self.is_edit_mode and not self.cb_template.currentData():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn Cấp độ (Mẫu) để khởi tạo Lớp!")
            self.cb_template.setFocus()
            return
        if not self.txt_name.text().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập Tên Lớp!")
            self.txt_name.setFocus()
            return
        if not self.cb_location.currentText().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn hoặc nhập Địa điểm!")
            self.cb_location.setFocus()
            return
        if not self.cb_schedule.currentText().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn hoặc nhập Lịch học!")
            self.cb_schedule.setFocus()
            return
        if not self.cb_time_slot.currentText().strip():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn hoặc nhập Giờ học!")
            self.cb_time_slot.setFocus()
            return
            
        ConfigService.add_new_location(self.cb_location.currentText())
        ConfigService.add_new_schedule(self.cb_schedule.currentText())
        ConfigService.add_new_time_slot(self.cb_time_slot.currentText())
        self.accept()

    def get_class_data(self) -> dict:
        """
        EN: Get data entered in the form.
        VI: Lấy dữ liệu được nhập trên form.
        """
        dt = self.date_start.date()
        month_year = f"{dt.month():02d}/{dt.year()}"
        
        data = {
            "class_code": self.txt_code.text().strip(),
            "class_name": self.txt_name.text().strip(),
            "location": self.cb_location.currentText().strip(),
            "room": self.txt_room.text().strip(),
            "session": self.cb_session.currentText().strip(),
            "schedule": self.cb_schedule.currentText().strip(),
            "time_slot": self.cb_time_slot.currentText().strip(),
            "start_month_year": month_year,
            "min_students": self.sb_min.value(),
            "max_students": self.sb_max.value(),
            "end_date": self.date_end.date().toPyDate()
        }
        
        if self.is_edit_mode and self.class_info:
            data["current_students"] = self.class_info.current_students
            data["class_status"] = getattr(self.class_info, 'class_status', 'Dự kiến')
        else:
            data["current_students"] = 0
            data["class_status"] = "Dự kiến"
            
        return data