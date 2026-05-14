from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QTableWidget, 
                             QLabel, QHeaderView, QTableWidgetItem, QMessageBox,
                             QComboBox, QApplication, QFileDialog, QGroupBox)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QColor
import os
import sys
import webbrowser
from datetime import datetime
import re
from apps.main_app.src.services.class_service import ClassService
from apps.main_app.src.services.core_google_api_service import GoogleApiService
from apps.main_app.src.services.class_wave_metadata_service import WaveMetadataService
from apps.main_app.src.models.entities import ClassInfo
from apps.main_app.src.views.class_dialog import ClassDialog
from apps.main_app.src.services.class_registration_service import RegistrationService
from apps.main_app.src.views.class_links_widget import ClassLinksWidget


class ClassPlanningTab(QWidget):
    """
    EN: Tab for planning classes, generating Google Forms, and importing registrations.
    VI: Tab lên kế hoạch lớp học, tạo Google Form và cập nhật lượt đăng ký.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_year = ""
        self.current_wave = ""
        self.settings = QSettings("SchoolTrackOrg", "SchoolTrack")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)
        layout.setSpacing(15)

        toolbar_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm theo Mã lớp, Tên lớp...")
        self.search_input.setFixedWidth(350)
        self.search_input.setStyleSheet("padding: 6px; font-size: 14px;")
        self.search_input.textChanged.connect(self.filter_table)
        
        self.btn_copy_form = QPushButton("📋 Copy cho Google Form")
        self.btn_copy_form.setStyleSheet("padding: 6px 15px; font-weight: bold; background-color: #10B981; color: white; border-radius: 5px;")
        self.btn_copy_form.clicked.connect(self.copy_for_google_form)

        self.btn_auto_form = QPushButton("🪄 Tự động tạo Form")
        self.btn_auto_form.setStyleSheet("padding: 6px 15px; font-weight: bold; background-color: #F59E0B; color: white; border-radius: 5px;")
        self.btn_auto_form.clicked.connect(self.auto_create_form)

        self.cb_import_mode = QComboBox()
        self.cb_import_mode.addItems(["1. Lọc cứng", "2. Cảnh báo", "3. Thông minh"])
        self.cb_import_mode.setCurrentIndex(self.settings.value("class_view/import_mode", 0, type=int))
        self.cb_import_mode.currentIndexChanged.connect(lambda i: self.settings.setValue("class_view/import_mode", i))

        self.btn_import_google_form = QPushButton("📥 Cập nhật SL Đăng ký")
        self.btn_import_google_form.setStyleSheet("padding: 6px 15px; font-weight: bold; background-color: #8B5CF6; color: white; border-radius: 5px;")
        self.btn_import_google_form.clicked.connect(self.import_google_form)

        self.btn_reload = QPushButton("🔄 Tải lại")
        self.btn_reload.clicked.connect(lambda: self.load_data(self.current_year, self.current_wave))

        self.btn_add = QPushButton("➕ Thêm")
        self.btn_add.setStyleSheet("padding: 6px 15px; font-weight: bold; background-color: #3B82F6; color: white; border-radius: 5px;")
        self.btn_add.clicked.connect(self.open_add_dialog)

        self.btn_edit = QPushButton("✏️ Sửa")
        self.btn_edit.setStyleSheet("padding: 6px 15px; font-weight: bold; background-color: #F59E0B; color: white; border-radius: 5px;")
        self.btn_edit.clicked.connect(self.open_edit_dialog)

        self.btn_delete = QPushButton("🗑️ Xóa")
        self.btn_delete.setStyleSheet("padding: 6px 15px; font-weight: bold; background-color: #EF4444; color: white; border-radius: 5px;")
        self.btn_delete.clicked.connect(self.delete_class)

        toolbar_layout.addWidget(self.search_input)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_copy_form)
        toolbar_layout.addWidget(self.btn_auto_form)
        toolbar_layout.addWidget(self.cb_import_mode)
        toolbar_layout.addWidget(self.btn_import_google_form)
        toolbar_layout.addWidget(self.btn_add)
        toolbar_layout.addWidget(self.btn_edit)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addWidget(self.btn_reload)

        layout.addLayout(toolbar_layout)

        self.links_widget = ClassLinksWidget(self)
        layout.addWidget(self.links_widget)

        self.table = QTableWidget()
        headers = ["Chọn", "Mã Lớp", "Tên Lớp", "Địa Điểm", "Phòng Học", "Buổi Học", "Lịch Học", "Giờ Học", "Khai Giảng", "Kết Thúc", "SL Min", "SL Max", "Đăng Ký"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setAlternatingRowColors(True)
        self.table.itemDoubleClicked.connect(self.open_edit_dialog)
        layout.addWidget(self.table)

        self.lbl_stats = QLabel("Thống kê: 0 lớp chính thức | 0 rổ dự kiến")
        self.lbl_stats.setStyleSheet("font-size: 14px; font-weight: bold; color: #4B5563;")
        layout.addWidget(self.lbl_stats)

    def load_data(self, year: str, wave: str) -> None:
        """
        EN: Fetch and display class data based on selected year and wave.
        VI: Nạp và hiển thị dữ liệu lớp học dựa trên niên khóa và đợt đã chọn.
        """
        self.current_year = year
        self.current_wave = wave
        
        is_all_waves = wave == "Tất cả"
        for widget in [self.btn_auto_form, self.btn_add, self.btn_edit, self.btn_delete, self.btn_import_google_form]:
            widget.setEnabled(not is_all_waves)
            
        self.links_widget.load_data(year, wave)

        if not year or year == "Chưa có dữ liệu" or not wave or wave == "Chưa có đợt":
            self.lbl_stats.setText("Trạng thái: Chưa có dữ liệu Lớp học.")
            self.table.setRowCount(0)
            return

        file_path = ClassService.get_file_path_for_year(year)
        if not os.path.exists(file_path):
            self.table.setRowCount(0)
            return

        try:
            all_classes = ClassService.get_classes_from_excel(file_path, None)
            display_classes = all_classes if is_all_waves else [c for c in all_classes if c.class_code in WaveMetadataService.get_class_codes_for_wave(year, wave)]
            
            self.table.setUpdatesEnabled(False)
            self.table.setRowCount(0)
            self.table.setRowCount(len(display_classes))
            
            for r, cls in enumerate(display_classes):
                item_check = QTableWidgetItem()
                item_check.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                item_check.setCheckState(Qt.CheckState.Unchecked)
                self.table.setItem(r, 0, item_check)
                
                item_code = QTableWidgetItem(cls.class_code)
                item_code.setData(Qt.ItemDataRole.UserRole, getattr(cls, 'class_status', 'Dự kiến'))
                self.table.setItem(r, 1, item_code)
                self.table.setItem(r, 2, QTableWidgetItem(cls.class_name))
                self.table.setItem(r, 3, QTableWidgetItem(cls.location))
                self.table.setItem(r, 4, QTableWidgetItem(getattr(cls, 'room', '')))
                self.table.setItem(r, 5, QTableWidgetItem(cls.session))
                self.table.setItem(r, 6, QTableWidgetItem(cls.schedule))
                self.table.setItem(r, 7, QTableWidgetItem(cls.time_slot))
                self.table.setItem(r, 8, QTableWidgetItem(cls.start_month_year))
                self.table.setItem(r, 9, QTableWidgetItem(cls.end_date.strftime("%d/%m/%Y") if cls.end_date else ""))
                self.table.setItem(r, 10, QTableWidgetItem(str(cls.min_students)))
                self.table.setItem(r, 11, QTableWidgetItem(str(cls.max_students)))
                
                item_current = QTableWidgetItem(str(cls.current_students))
                item_current.setForeground(QColor("#16A34A") if cls.current_students >= cls.min_students else QColor("#DC2626"))
                self.table.setItem(r, 12, item_current)
                
            self.table.setUpdatesEnabled(True)
            self.filter_table()
            
            du_kien = sum(1 for c in display_classes if getattr(c, 'class_status', 'Dự kiến') == "Dự kiến")
            self.lbl_stats.setText(f"Thống kê: {len(display_classes) - du_kien} lớp chính thức | {du_kien} rổ dự kiến")
        except Exception as e:
            # EN: Catch data parsing errors
            # VI: Bắt lỗi đọc dữ liệu Excel
            QMessageBox.warning(self, "Lỗi tải dữ liệu", str(e))

    def filter_table(self, text: str = "") -> None:
        """
        EN: Filter table rows by class code or name.
        VI: Lọc các dòng trong bảng theo mã hoặc tên lớp.
        """
        search_text = self.search_input.text().lower().strip()
        for row in range(self.table.rowCount()):
            code = self.table.item(row, 1)
            name = self.table.item(row, 2)
            if code and name:
                match = search_text in code.text().lower() or search_text in name.text().lower()
                self.table.setRowHidden(row, not match)

    def copy_for_google_form(self) -> None:
        """
        EN: Copy selected classes to clipboard.
        VI: Copy các lớp được chọn vào Clipboard.
        """
        selected = []
        for r in range(self.table.rowCount()):
            if self.table.item(r, 0).checkState() == Qt.CheckState.Checked:
                selected.append(f"{self.table.item(r, 2).text()} - {self.table.item(r, 5).text()} {self.table.item(r, 6).text()} ({self.table.item(r, 7).text()}) - {self.table.item(r, 3).text()} [Mã: {self.table.item(r, 1).text()}]")
        if selected:
            QApplication.clipboard().setText("\n".join(selected))
            QMessageBox.information(self, "Thành công", f"Đã copy {len(selected)} lớp!")

    def auto_create_form(self) -> None:
        """Gọi API Google Apps Script để tự động tạo Form và Sheet."""
        if not self.current_year or self.current_year == "Chưa có dữ liệu" or not self.current_wave or self.current_wave == "Chưa có đợt" or self.current_wave == "Tất cả":
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một Đợt cụ thể để tạo Form!")
            return

        web_app_url = self.settings.value("gas/web_app_url", "")
        template_id = str(self.settings.value("gas/template_id", "")).strip()
        secret = self.settings.value("gas/secret", "")
        
        if "docs.google.com/forms/d/" in template_id:
            match = re.search(r"/d/([a-zA-Z0-9-_]+)", template_id)
            if match:
                template_id = match.group(1)
                self.settings.setValue("gas/template_id", template_id)
        
        if not web_app_url or not template_id or not secret:
            QMessageBox.information(self, "Thiết lập", "Bạn chưa cấu hình API Google Form. Vui lòng thiết lập ở hộp thoại tiếp theo.")
            self.open_gas_config_dialog()
            return
            
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
                formatted_str = f"{class_name} - {session} {schedule} ({time_slot}) - {location} [Mã: {class_code}]"
                selected_classes.append(formatted_str)
                
        if not selected_classes:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tick chọn ít nhất 1 lớp (ở cột Chọn) để đưa vào Form!")
            return
            
        reply = QMessageBox.question(self, "Xác nhận", f"Hệ thống sẽ ra lệnh nhân bản Form Mẫu để tạo Form mới cho đợt '{self.current_wave}' với {len(selected_classes)} lớp học.\n\nQuá trình này có thể mất khoảng 10-15 giây. Bạn có muốn tiếp tục?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            response = GoogleApiService.auto_create_google_form(web_app_url, secret, template_id, self.current_wave, selected_classes)
            QApplication.restoreOverrideCursor()
            
            if response.get("status") == "success":
                self.links_widget.set_links(response.get("form_url", ""), response.get("sheet_url", ""))
                self.links_widget.save_wave_links()
                QMessageBox.information(self, "Thành công", f"Đã tự động tạo Form và Sheet thành công cho '{self.current_wave}'!\nLink đã được lưu vào hệ thống.")
            else:
                QMessageBox.critical(self, "Lỗi API", f"Không thể tạo Form:\n{response.get('message', 'Lỗi không xác định hoặc cấu hình sai')}")
        
    def import_google_form(self) -> None:
        """Đọc file Excel Google Form thô để đếm và cập nhật số lượng đăng ký lên Tab 1."""
        if not self.current_year or self.current_year == "Chưa có dữ liệu" or not self.current_wave or self.current_wave == "Chưa có đợt":
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn Niên khóa và Đợt trước!")
            return
            
        if self.current_wave == "Tất cả":
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một Đợt cụ thể để hệ thống biết đang cập nhật cho đợt nào!")
            return

        from apps.main_app.src.services.student_service import StudentService
        try:
            students_db = StudentService.get_students_from_excel(StudentService.get_file_path())
        except Exception as e:
            QMessageBox.warning(self, "Lỗi dữ liệu", f"Không thể tải danh sách Sinh viên gốc để đối chiếu:\n{e}")
            return
            
        mode_idx = self.cb_import_mode.currentIndex() + 1

        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file Excel tải từ Google Form", "", "Excel Files (*.xlsx *.xls)")
        
        if file_path:
            try:
                counts, warnings = RegistrationService.count_registrations_from_file(file_path, mode=mode_idx, students_db=students_db)
                if not counts:
                    msg = "Không tìm thấy dữ liệu đăng ký hợp lệ trong file!\n\nNguyên nhân có thể do:\n1. File Excel không có cột nào chứa định dạng '[Mã: LNH...]'.\n2. TOÀN BỘ Mã Sinh Viên trong form đều không có trong 'Danh sách SV gốc' nên đã bị hệ thống lọc bỏ."
                    if warnings:
                        msg += f"\n\n⚠️ Hệ thống đã loại bỏ {len(warnings)} đăng ký do MSV không hợp lệ:\n" + "\n".join(warnings[:5])
                    QMessageBox.warning(self, "Cảnh báo", msg)
                    return
                    
                class_file_path = ClassService.get_file_path_for_year(self.current_year)
                
                ClassService.update_registration_counts(class_file_path, self.current_wave, counts)
                self.load_data(self.current_year, self.current_wave)
                
                msg = f"Cập nhật thành công số lượng cho {len(counts)} rổ dự kiến:\n\n"
                for code, count in counts.items():
                    msg += f"• {code}: {count} SV\n"
                    
                if warnings:
                    msg += f"\n⚠️ CÓ {len(warnings)} LỖI MSV TRONG FORM (Đã bỏ qua):\n"
                    msg += "\n".join(warnings[:10])
                    if len(warnings) > 10:
                        msg += f"\n... và {len(warnings) - 10} trường hợp gõ sai MSV khác."
                        
                QMessageBox.information(self, "Thành công", msg)
            except PermissionError:
                QMessageBox.warning(self, "Lỗi truy cập", "File Excel đang được mở.\nVui lòng đóng file trước khi cập nhật!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Có lỗi xảy ra khi đọc file:\n{e}")

    def open_form_link(self) -> None:
        link = self.txt_form_link.text().strip()
        if "script.google.com" in link:
            QMessageBox.warning(self, "Nhầm lẫn Link", "Đây là link API của Google Script (Nhân viên ảo), không phải link Google Form!\n\nVui lòng dán link này vào phần '⚙️ Cấu hình API' và nhấn nút '🪄 Tự động tạo Form'.")
            return
        if link and "script" not in link: webbrowser.open("https://" + link if not link.startswith("http") else link)
        
    def open_sheet_link(self) -> None:
        link = self.txt_sheet_link.text().strip()
        if "script.google.com" in link:
            QMessageBox.warning(self, "Nhầm lẫn Link", "Đây là link API của Google Script, không phải link Google Sheet!\n\nVui lòng nhấn nút '🪄 Tự động tạo Form' để phần mềm tự sinh ra link Sheet chuẩn xác.")
            return
        if link and "script" not in link: webbrowser.open("https://" + link if not link.startswith("http") else link)

    def download_sheet_file(self) -> None:
        """Tải file Google Sheet về máy dưới dạng file Excel."""
        sheet_link = self.txt_sheet_link.text().strip()
        if not sheet_link:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập link Google Sheet trước khi tải!")
            return

        save_dir = QFileDialog.getExistingDirectory(self, "Chọn thư mục để lưu file Excel")
        if not save_dir:
            return

        date_str = datetime.now().strftime("%Y-%m-%d")
        wave_str = self.current_wave.replace(" ", "_") if self.current_wave and self.current_wave != "Tất cả" else "Tong_hop"
        file_name = f"[{date_str}]_KetQuaDangKy_{wave_str}.xlsx"
        save_path = os.path.join(save_dir, file_name)

        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            success = ClassService.download_google_sheet_as_excel(sheet_link, save_path)
            QApplication.restoreOverrideCursor()

            if success:
                reply = QMessageBox.information(self, "Tải thành công", f"Đã tải file thành công!\n\nĐường dẫn: {save_path}\n\nBạn có muốn mở thư mục chứa file không?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
                if reply == QMessageBox.StandardButton.Yes:
                    if sys.platform == "win32": os.startfile(save_dir)
                    else:
                        import subprocess
                        opener = "open" if sys.platform == "darwin" else "xdg-open"
                        subprocess.run([opener, save_dir])
            else:
                QMessageBox.critical(self, "Tải thất bại", "Không thể tải file từ Google Sheet!\n\nNguyên nhân thường gặp:\n1. File đang bị khóa (Restricted). Bạn cần mở Google Sheet bằng trình duyệt, chọn 'Chia sẻ' và đổi quyền thành 'Bất kỳ ai có đường liên kết'.\n2. Link không hợp lệ hoặc lỗi mạng.")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Lỗi", f"Có lỗi không xác định xảy ra:\n{e}")

    def save_wave_links(self) -> None:
        if self.current_year and self.current_wave:
            ClassService.save_wave_links(self.current_year, self.current_wave, self.txt_form_link.text(), self.txt_sheet_link.text())
            QMessageBox.information(self, "Thành công", "Đã lưu cấu hình link!")

    def open_add_dialog(self) -> None:
        dialog = ClassDialog(self, existing_codes=[self.table.item(r, 1).text() for r in range(self.table.rowCount()) if self.table.item(r, 1)])
        if dialog.exec():
            try:
                data = dialog.get_class_data()
                data["year_code"] = self.current_year
                ClassService.save_class_to_excel(ClassService.get_file_path_for_year(self.current_year), self.current_wave, ClassInfo(**data))
                self.load_data(self.current_year, self.current_wave)
            except Exception as e:
                # EN: Catch file lock or save errors
                # VI: Bắt lỗi khóa file hoặc lưu dữ liệu
                QMessageBox.warning(self, "Lỗi", str(e))

    def open_edit_dialog(self, item=None) -> None:
        """Mở hộp thoại sửa thông tin lớp học đang chọn."""
        r = self.table.currentRow()
        if r < 0: return
        
        def get_item_text(col: int) -> str:
            it = self.table.item(r, col)
            return it.text() if it else ""
            
        end_date = None
        end_date_str = get_item_text(9)
        if end_date_str:
            try: end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date()
            except ValueError: pass
                
        status_data = self.table.item(r, 1).data(Qt.ItemDataRole.UserRole)
        class_status = status_data if status_data else "Dự kiến"
                
        class_info = ClassInfo(
            class_code=get_item_text(1),
            year_code=self.current_year,
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
            data["year_code"] = self.current_year
            try:
                updated_class = ClassInfo(**data)
                file_path = ClassService.get_file_path_for_year(self.current_year)
                ClassService.save_class_to_excel(file_path, self.current_wave, updated_class)
                QMessageBox.information(self, "Thành công", f"Đã cập nhật lớp:\n{updated_class.class_code} - {updated_class.class_name}")
                self.load_data(self.current_year, self.current_wave)
            except PermissionError:
                QMessageBox.warning(self, "Lỗi truy cập", "File Excel đang được mở bởi một chương trình khác (ví dụ: MS Excel).\nVui lòng đóng file Excel trước khi lưu!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể lưu dữ liệu:\n{e}")
        
    def delete_class(self) -> None:
        r = self.table.currentRow()
        if r >= 0 and self.table.item(r, 12).text() == "0":
            reply = QMessageBox.question(self, "Xác nhận xóa", f"Bạn có chắc chắn muốn xóa lớp dự kiến:\n{self.table.item(r, 1).text()}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                ClassService.delete_class_from_excel(ClassService.get_file_path_for_year(self.current_year), self.current_year, self.current_wave, self.table.item(r, 1).text())
                self.load_data(self.current_year, self.current_wave)
        elif r >= 0:
            QMessageBox.warning(self, "Từ chối Xóa", "Không thể xóa lớp đã có sinh viên đăng ký!\nVui lòng chuyển sinh viên sang lớp khác trước khi xóa.")