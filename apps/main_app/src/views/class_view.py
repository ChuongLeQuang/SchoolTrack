from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QLabel, QHeaderView, QTableWidgetItem, QMessageBox,
                             QComboBox, QInputDialog, QStackedWidget, QApplication, QFileDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
import os
from apps.main_app.src.services.class_service import ClassService
from apps.main_app.src.models.entities import ClassInfo
from apps.main_app.src.views.class_dialog import ClassDialog
from apps.main_app.src.services.registration_service import RegistrationService


class ClassView(QWidget):
    """
    EN: Class Management UI containing data table and toolbars.
    VI: Giao diện quản lý Lớp học chứa bảng dữ liệu và thanh công cụ.
    """
    
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self._load_academic_years()
        # Đợi giao diện dựng xong rồi mới nạp dữ liệu
        QTimer.singleShot(500, self.load_data)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # --- GLOBAL CONTEXT: Chọn Niên Khóa ---
        year_layout = QHBoxLayout()
        lbl_year = QLabel("Niên Khóa:")
        lbl_year.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.cb_academic_year = QComboBox()
        self.cb_academic_year.setStyleSheet("padding: 5px; font-size: 14px;")
        self.cb_academic_year.setMinimumWidth(200)
        self.cb_academic_year.currentTextChanged.connect(self.load_data)
        
        self.btn_new_year = QPushButton("➕ Tạo Niên Khóa Mới")
        self.btn_new_year.setStyleSheet("padding: 5px 10px; font-size: 13px; background-color: #10B981; color: white; border: none; border-radius: 4px;")
        self.btn_new_year.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_year.clicked.connect(self.create_new_year)
        
        year_layout.addWidget(lbl_year)
        year_layout.addWidget(self.cb_academic_year)
        year_layout.addWidget(self.btn_new_year)
        year_layout.addStretch()
        
        layout.addLayout(year_layout)

        # --- DYNAMIC TITLE LÀM HEADER CHO GIAI ĐOẠN ---
        self.lbl_phase_title = QLabel("📝 1. Kế hoạch Dự kiến")
        self.lbl_phase_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2563EB; padding: 10px 0;")
        layout.addWidget(self.lbl_phase_title)
        
        # --- KHOANG CHỨA NỘI DUNG (THAY THẾ TABS BẰNG STACKED WIDGET) ---
        self.inner_stack = QStackedWidget()
        self.inner_stack.addWidget(self._setup_tab_planning())
        self.inner_stack.addWidget(self._setup_tab_sync_accounting())
        self.inner_stack.addWidget(self._setup_tab_finalization())
        
        layout.addWidget(self.inner_stack)
        self.setLayout(layout)

    def _setup_tab_planning(self) -> QWidget:
        """Giai đoạn 1: Lên kế hoạch (Tạo lớp nháp)."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)

        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm theo Mã lớp, Tên lớp...")
        self.search_input.setFixedWidth(350)
        self.search_input.setStyleSheet("padding: 6px; font-size: 14px;")
        
        self.btn_copy_form = QPushButton("📋 Copy cho Google Form")
        self.btn_copy_form.setStyleSheet("padding: 6px 15px; font-weight: bold; font-size: 14px; background-color: #10B981; color: white; border: none; border-radius: 5px;")
        self.btn_copy_form.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_form.clicked.connect(self.copy_for_google_form)

        self.btn_import_google_form = QPushButton("📥 Cập nhật SL Đăng ký")
        self.btn_import_google_form.setStyleSheet("padding: 6px 15px; font-weight: bold; font-size: 14px; background-color: #8B5CF6; color: white; border: none; border-radius: 5px;")
        self.btn_import_google_form.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import_google_form.clicked.connect(self.import_google_form)

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
        self.btn_delete.clicked.connect(self.delete_class)

        self.search_input.textChanged.connect(self.filter_table)

        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_copy_form)
        toolbar_layout.addWidget(self.btn_import_google_form)
        toolbar_layout.addWidget(self.btn_add)
        toolbar_layout.addWidget(self.btn_edit)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addWidget(self.btn_reload)

        layout.addLayout(toolbar_layout)

        # Bảng dữ liệu Lớp dự kiến
        self.table = QTableWidget()
        headers = ["Chọn", "Mã Lớp", "Tên Lớp", "Địa Điểm", "Phòng Học", "Buổi Học", "Lịch Học", "Giờ Học", "Khai Giảng", "Kết Thúc", "SL Min", "SL Max", "Đăng Ký"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(11, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(12, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setStyleSheet("font-size: 13px;")
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self.open_edit_dialog)
        layout.addWidget(self.table)

        # Footer
        self.lbl_stats = QLabel("Thống kê: 0 lớp chính thức | 0 rổ dự kiến")
        self.lbl_stats.setStyleSheet("font-size: 14px; font-weight: bold; color: #4B5563;")
        layout.addWidget(self.lbl_stats)

        tab.setLayout(layout)
        return tab

    def _setup_tab_sync_accounting(self) -> QWidget:
        """Giai đoạn 2: Đối chiếu Kế toán."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)

        # 1. Toolbar
        sync_toolbar = QHBoxLayout()
        self.btn_start_sync = QPushButton("📂 Chọn & Đối chiếu File Kế toán")
        self.btn_start_sync.setStyleSheet("padding: 8px 20px; font-weight: bold; font-size: 15px; background-color: #8B5CF6; color: white; border: none; border-radius: 5px;")
        self.btn_start_sync.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start_sync.clicked.connect(self.start_accounting_sync)
        
        sync_toolbar.addWidget(self.btn_start_sync)
        sync_toolbar.addStretch()
        layout.addLayout(sync_toolbar)

        # 2. Bảng kết quả xử lý
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

        # 3. Dòng trạng thái
        self.lbl_sync_stats = QLabel("Trạng thái: Sẵn sàng để đối chiếu.")
        self.lbl_sync_stats.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.lbl_sync_stats)

        tab.setLayout(layout)
        return tab

    def _setup_tab_finalization(self) -> QWidget:
        """Giai đoạn 3: Chốt Lớp & Phân bổ."""
        tab = QWidget()
        layout = QVBoxLayout()
        
        lbl_info = QLabel("Giao diện kiểm tra số lượng và Chốt Mở/Hủy lớp sẽ được triển khai tại đây.")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_info.setStyleSheet("font-size: 16px; color: #6B7280;")
        
        layout.addWidget(lbl_info)
        tab.setLayout(layout)
        return tab

    def set_active_screen(self, index: int) -> None:
        """Chuyển đổi giao diện dựa trên lựa chọn từ menu Sidebar."""
        self.inner_stack.setCurrentIndex(index)
        if index == 0:
            self.lbl_phase_title.setText("📝 1. Kế hoạch Dự kiến")
        elif index == 1:
            self.lbl_phase_title.setText("💰 2. Đối chiếu Kế toán")
        elif index == 2:
            self.lbl_phase_title.setText("✅ 3. Chốt Lớp & Phân bổ")

    def _load_academic_years(self) -> None:
        """Quét thư mục data để lấy danh sách các file Niên khóa."""
        self.cb_academic_year.blockSignals(True)
        self.cb_academic_year.clear()
        
        years = ClassService.get_academic_years()
        if not years:
            years.append("Chưa có dữ liệu")
            
        self.cb_academic_year.addItems(years)
        self.cb_academic_year.blockSignals(False)

    def load_data(self) -> None:
        """Đọc danh sách Lớp học và đổ vào bảng."""
        current_year = self.cb_academic_year.currentText()
        if not current_year or current_year == "Chưa có dữ liệu":
            self.lbl_stats.setText("Trạng thái: Chưa có dữ liệu Niên khóa nào.")
            self.table.setRowCount(0)
            return

        file_path = ClassService.get_file_path_for_year(current_year)
        
        if not os.path.exists(file_path):
            self.lbl_stats.setText(f"Trạng thái: Không tìm thấy file 'Quan Ly Lop Hoc {current_year}.xlsx'")
            return

        try:
            classes = ClassService.get_classes_from_excel(file_path)
            self.table.setRowCount(len(classes))
            
            for row_idx, cls in enumerate(classes):
                item_check = QTableWidgetItem()
                item_check.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                item_check.setCheckState(Qt.CheckState.Unchecked)
                self.table.setItem(row_idx, 0, item_check)
                
                item_code = QTableWidgetItem(cls.class_code)
                item_code.setData(Qt.ItemDataRole.UserRole, getattr(cls, 'class_status', 'Dự kiến'))
                self.table.setItem(row_idx, 1, item_code)
                self.table.setItem(row_idx, 2, QTableWidgetItem(cls.class_name))
                self.table.setItem(row_idx, 3, QTableWidgetItem(cls.location))
                room_val = getattr(cls, 'room', '')
                self.table.setItem(row_idx, 4, QTableWidgetItem("" if str(room_val).lower() == "none" else room_val))
                self.table.setItem(row_idx, 5, QTableWidgetItem(cls.session))
                self.table.setItem(row_idx, 6, QTableWidgetItem(cls.schedule))
                self.table.setItem(row_idx, 7, QTableWidgetItem(cls.time_slot))
                self.table.setItem(row_idx, 8, QTableWidgetItem(cls.start_month_year))
                
                end_date_str = cls.end_date.strftime("%d/%m/%Y") if cls.end_date else ""
                self.table.setItem(row_idx, 9, QTableWidgetItem(end_date_str))
                
                item_min = QTableWidgetItem(str(cls.min_students))
                item_min.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, 10, item_min)

                item_max = QTableWidgetItem(str(cls.max_students))
                item_max.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, 11, item_max)
                
                item_current = QTableWidgetItem(str(cls.current_students))
                item_current.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Tô màu và làm đậm cho cột Đăng ký
                font = item_current.font()
                font.setBold(True)
                item_current.setFont(font)
                
                if cls.current_students < cls.min_students:
                    item_current.setForeground(QColor("#DC2626"))  # Đỏ
                else:
                    item_current.setForeground(QColor("#16A34A"))  # Xanh lá
                    
                self.table.setItem(row_idx, 12, item_current)
                
            # Thống kê minh bạch
            du_kien = sum(1 for c in classes if str(getattr(c, 'class_status', 'Dự kiến')).strip().lower() == "dự kiến")
            chinh_thuc = len(classes) - du_kien
            
            self.lbl_stats.setText(f"Thống kê: {chinh_thuc} lớp chính thức | {du_kien} rổ dự kiến")
        except Exception as e:
            QMessageBox.warning(self, "Lỗi tải dữ liệu", f"Không thể tải dữ liệu lớp học:\n{e}")

    def create_new_year(self) -> None:
        """Tạo file Excel mới cho Niên khóa tiếp theo."""
        year, ok = QInputDialog.getText(self, "Tạo Niên Khóa", "Nhập niên khóa mới (VD: 2025-2026):")
        if ok and year.strip():
            year = year.strip()
            file_path = ClassService.get_file_path_for_year(year)
            
            try:
                if ClassService.create_academic_year_file(file_path):
                    QMessageBox.information(self, "Thành công", f"Đã tạo file dữ liệu cho niên khóa {year}!")
                    self._load_academic_years()
                    self.cb_academic_year.setCurrentText(year)
                else:
                    QMessageBox.warning(self, "Lỗi", f"Niên khóa {year} đã tồn tại!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể tạo file:\n{e}")

    def filter_table(self) -> None:
        """Lọc dữ liệu lớp học theo từ khóa trên bảng."""
        search_text = self.search_input.text().lower().strip()
        for row in range(self.table.rowCount()):
            item_code = self.table.item(row, 1)
            item_name = self.table.item(row, 2)
            if not item_code or not item_name: continue

            match_search = (search_text in item_code.text().lower() or search_text in item_name.text().lower())
            self.table.setRowHidden(row, not match_search)

    def open_add_dialog(self) -> None:
        """Mở hộp thoại thêm lớp dự kiến mới."""
        current_year = self.cb_academic_year.currentText()
        if not current_year or current_year == "Chưa có dữ liệu":
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tạo Niên khóa trước khi thêm lớp!")
            return

        existing_codes = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 1)
            if item: existing_codes.append(item.text().strip())

        dialog = ClassDialog(self, existing_codes=existing_codes)
        if dialog.exec():
            data = dialog.get_class_data()
            data["year_code"] = current_year
            
            # Kiểm tra trùng lặp mã lớp trên bảng
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 1)
                if item and item.text().strip() == data["class_code"]:
                    QMessageBox.warning(self, "Lỗi", f"Mã Lớp '{data['class_code']}' đã tồn tại trong danh sách!")
                    return
            
            try:
                class_info = ClassInfo(**data)
                file_path = ClassService.get_file_path_for_year(current_year)
                
                # Lưu xuống Excel và tải lại bảng
                ClassService.save_class_to_excel(file_path, class_info)
                QMessageBox.information(self, "Thành công", f"Đã thêm lớp dự kiến:\n{class_info.class_code} - {class_info.class_name}")
                QTimer.singleShot(50, self.load_data)
            except PermissionError:
                QMessageBox.warning(self, "Lỗi truy cập", "File Excel đang được mở bởi một chương trình khác (ví dụ: MS Excel).\nVui lòng đóng file Excel trước khi lưu!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể lưu dữ liệu:\n{e}")

    def delete_class(self) -> None:
        """Xóa lớp dự kiến đang chọn (Chỉ khi chưa có ai đăng ký)."""
        current_year = self.cb_academic_year.currentText()
        if not current_year or current_year == "Chưa có dữ liệu":
            return
            
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một lớp để xóa!")
            return
            
        item_code = self.table.item(current_row, 1)
        item_name = self.table.item(current_row, 2)
        item_current = self.table.item(current_row, 12) # Cột Đăng Ký
        
        if not item_code or not item_name or not item_current:
            return
            
        class_code = item_code.text()
        class_name = item_name.text()
        current_students = int(item_current.text()) if item_current.text().isdigit() else 0
        
        if current_students > 0:
            QMessageBox.warning(self, "Từ chối Xóa", "Không thể xóa lớp đã có sinh viên đăng ký!\nVui lòng chuyển sinh viên sang lớp khác trước khi xóa.")
            return
            
        reply = QMessageBox.question(self, "Xác nhận xóa", f"Bạn có chắc chắn muốn xóa lớp dự kiến:\n{class_code} - {class_name}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            file_path = ClassService.get_file_path_for_year(current_year)
            try:
                if ClassService.delete_class_from_excel(file_path, class_code):
                    QMessageBox.information(self, "Thành công", f"Đã xóa lớp {class_code} thành công!")
                    QTimer.singleShot(50, self.load_data)
            except PermissionError:
                QMessageBox.warning(self, "Lỗi truy cập", "File Excel đang mở.\nVui lòng đóng file Excel trước khi xóa!")

    def open_edit_dialog(self, item=None) -> None:
        """Mở hộp thoại sửa thông tin lớp học đang chọn."""
        current_year = self.cb_academic_year.currentText()
        if not current_year or current_year == "Chưa có dữ liệu":
            return
            
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một lớp để sửa!")
            return
            
        def get_item_text(col: int) -> str:
            it = self.table.item(current_row, col)
            return it.text() if it else ""
            
        end_date = None
        end_date_str = get_item_text(9)
        if end_date_str:
            from datetime import datetime
            try: end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date()
            except ValueError: pass
                
        status_data = self.table.item(current_row, 1).data(Qt.ItemDataRole.UserRole)
        class_status = status_data if status_data else "Dự kiến"
                
        class_info = ClassInfo(
            class_code=get_item_text(1),
            year_code=current_year,
            class_name=get_item_text(2),
            location=get_item_text(3),
            room=get_item_text(4),
            session=get_item_text(5),
            schedule=get_item_text(6),
            time_slot=get_item_text(7),
            start_month_year=get_item_text(8),
            end_date=end_date,
            min_students=int(get_item_text(10)) if get_item_text(10).isdigit() else 0,
            max_students=int(get_item_text(11)) if get_item_text(11).isdigit() else 0,
            current_students=int(get_item_text(12)) if get_item_text(12).isdigit() else 0,
            class_status=class_status
        )
        
        dialog = ClassDialog(self, class_info=class_info)
        if dialog.exec():
            data = dialog.get_class_data()
            data["year_code"] = current_year
            try:
                updated_class = ClassInfo(**data)
                file_path = ClassService.get_file_path_for_year(current_year)
                
                ClassService.save_class_to_excel(file_path, updated_class)
                QMessageBox.information(self, "Thành công", f"Đã cập nhật lớp:\n{updated_class.class_code} - {updated_class.class_name}")
                QTimer.singleShot(50, self.load_data)
            except PermissionError:
                QMessageBox.warning(self, "Lỗi truy cập", "File Excel đang được mở bởi một chương trình khác (ví dụ: MS Excel).\nVui lòng đóng file Excel trước khi lưu!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể lưu dữ liệu:\n{e}")

    def copy_for_google_form(self) -> None:
        """Copy các lớp đã chọn (tick) vào Clipboard để dán vào Google Form."""
        selected_classes = []
        for row in range(self.table.rowCount()):
            item_check = self.table.item(row, 0)
            if item_check and item_check.checkState() == Qt.CheckState.Checked:
                class_code = self.table.item(row, 1).text()
                class_name = self.table.item(row, 2).text()
                location = self.table.item(row, 3).text()
                session = self.table.item(row, 5).text()
                schedule = self.table.item(row, 6).text()
                time_slot = self.table.item(row, 7).text()
                
                # Format chuẩn: Tiếng Anh Level 1 - Tối 2-4-6 (18:00 - 20:00) - Cơ sở Q9 [Mã: LNH0825NE]
                formatted_str = f"{class_name} - {session} {schedule} ({time_slot}) - {location} [Mã: {class_code}]"
                selected_classes.append(formatted_str)
                
        if not selected_classes:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tick chọn ít nhất 1 lớp (ở cột Chọn) để copy!")
            return
            
        final_text = "\n".join(selected_classes)
        QApplication.clipboard().setText(final_text)
        QMessageBox.information(
            self, "Thành công", 
            f"Đã copy {len(selected_classes)} lớp vào Clipboard!\nBạn có thể nhấn Ctrl+V để dán thẳng vào phần tùy chọn của Google Form."
        )

    def import_google_form(self) -> None:
        """Đọc file Excel Google Form thô để đếm và cập nhật số lượng đăng ký lên Tab 1."""
        current_year = self.cb_academic_year.currentText()
        if not current_year or current_year == "Chưa có dữ liệu":
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tạo Niên khóa trước!")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file Excel tải từ Google Form",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            try:
                counts = RegistrationService.count_registrations_from_file(file_path)
                if not counts:
                    QMessageBox.information(self, "Thông báo", "Không tìm thấy dữ liệu đăng ký hợp lệ trong file!")
                    return
                    
                class_file_path = ClassService.get_file_path_for_year(current_year)
                
                ClassService.update_registration_counts(class_file_path, counts)
                self.load_data()
                
                msg = f"Cập nhật thành công số lượng cho {len(counts)} rổ dự kiến:\n\n"
                for code, count in counts.items():
                    msg += f"• {code}: {count} SV\n"
                QMessageBox.information(self, "Thành công", msg)
            except PermissionError:
                QMessageBox.warning(self, "Lỗi truy cập", "File Excel đang được mở.\nVui lòng đóng file trước khi cập nhật!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Có lỗi xảy ra khi đọc file:\n{e}")

    def start_accounting_sync(self) -> None:
        """Bắt đầu quy trình đối chiếu file Excel từ Kế toán."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file Excel danh sách sinh viên đã đóng tiền",
            "",
            "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            QMessageBox.information(self, "Thông báo", f"Đã chọn file:\n{file_path}\n\nTính năng xử lý file sẽ được phát triển ở bước tiếp theo!")
            # TODO: Gọi RegistrationService để xử lý file tại đây