from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QMessageBox, QComboBox, QInputDialog, QStackedWidget, QGroupBox)
from PyQt6.QtCore import Qt, QSettings
from apps.main_app.src.services.class_service import ClassService
from apps.main_app.src.views.class_planning_tab import ClassPlanningTab
from apps.main_app.src.views.accounting_sync_tab import AccountingSyncTab


class ClassView(QWidget):
    """
    EN: Class Management UI container (Year/Wave selection & Tabs).
    VI: Giao diện vùng chứa Quản lý Lớp học (Điều phối Chọn Niên khóa/Đợt & Tabs).
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.is_data_loaded = False
        self.settings = QSettings("SchoolTrackOrg", "SchoolTrack")
        self._setup_ui()
        self._load_academic_years()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        global_group = QGroupBox("📌 Quản lý Niên Khóa & Đợt (Thuộc tính chung)")
        global_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold; font-size: 14px;
                margin-top: 10px; padding-top: 15px; padding-bottom: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        year_layout = QHBoxLayout()
        lbl_year = QLabel("Niên Khóa:")
        lbl_year.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        self.cb_academic_year = QComboBox()
        self.cb_academic_year.setStyleSheet("padding: 5px; font-size: 14px;")
        self.cb_academic_year.setMinimumWidth(200)
        self.cb_academic_year.currentTextChanged.connect(self._on_year_changed)
        
        self.btn_new_year = QPushButton("➕ Tạo Niên Khóa Mới")
        self.btn_new_year.setStyleSheet("padding: 5px 10px; font-size: 13px; background-color: #10B981; color: white; border: none; border-radius: 4px;")
        self.btn_new_year.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_year.clicked.connect(self.create_new_year)
        
        lbl_wave = QLabel("Đợt:")
        lbl_wave.setStyleSheet("font-size: 14px; font-weight: bold; margin-left: 15px;")
        
        self.cb_wave = QComboBox()
        self.cb_wave.setStyleSheet("padding: 5px; font-size: 14px;")
        self.cb_wave.setMinimumWidth(150)
        self.cb_wave.currentTextChanged.connect(self.load_data)
        
        self.btn_new_wave = QPushButton("➕ Đợt")
        self.btn_new_wave.setToolTip("Tạo Đợt mới")
        self.btn_new_wave.setStyleSheet("padding: 5px 10px; font-size: 13px; background-color: #2563EB; color: white; border: none; border-radius: 4px;")
        self.btn_new_wave.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new_wave.clicked.connect(self.create_new_wave)

        self.btn_rename_wave = QPushButton("✏️ Sửa Tên")
        self.btn_rename_wave.setToolTip("Đổi tên Đợt đang chọn")
        self.btn_rename_wave.setStyleSheet("padding: 5px 10px; font-size: 13px; background-color: #F59E0B; color: white; border: none; border-radius: 4px;")
        self.btn_rename_wave.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_rename_wave.clicked.connect(self.rename_current_wave)

        self.btn_delete_wave = QPushButton("🗑️ Xóa")
        self.btn_delete_wave.setToolTip("Xóa Đợt đang chọn")
        self.btn_delete_wave.setStyleSheet("padding: 5px 10px; font-size: 13px; background-color: #DC2626; color: white; border: none; border-radius: 4px;")
        self.btn_delete_wave.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete_wave.clicked.connect(self.delete_current_wave)

        year_layout.addWidget(lbl_year)
        year_layout.addWidget(self.cb_academic_year)
        year_layout.addWidget(self.btn_new_year)
        year_layout.addWidget(lbl_wave)
        year_layout.addWidget(self.cb_wave)
        year_layout.addWidget(self.btn_new_wave)
        year_layout.addWidget(self.btn_rename_wave)
        year_layout.addWidget(self.btn_delete_wave)
        year_layout.addStretch()
        
        global_group.setLayout(year_layout)
        layout.addWidget(global_group)

        self.lbl_phase_title = QLabel("📝 1. Kế hoạch Dự kiến")
        self.lbl_phase_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2563EB; padding: 10px 0;")
        layout.addWidget(self.lbl_phase_title)
        
        self.inner_stack = QStackedWidget()
        self.planning_tab = ClassPlanningTab(self)
        self.accounting_tab = AccountingSyncTab(self)
        self.inner_stack.addWidget(self.planning_tab)
        self.inner_stack.addWidget(self.accounting_tab)
        self.inner_stack.addWidget(self._setup_tab_finalization())
        
        layout.addWidget(self.inner_stack)
        self.setLayout(layout)

    def _setup_tab_finalization(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()
        lbl_info = QLabel("Giao diện kiểm tra số lượng và Chốt Mở/Hủy lớp sẽ được triển khai tại đây.")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_info.setStyleSheet("font-size: 16px; color: #6B7280;")
        layout.addWidget(lbl_info)
        tab.setLayout(layout)
        return tab

    def set_active_screen(self, index: int) -> None:
        self.inner_stack.setCurrentIndex(index)
        if index == 0:
            self.lbl_phase_title.setText("📝 1. Kế hoạch Dự kiến")
        elif index == 1:
            self.lbl_phase_title.setText("💰 2. Đối chiếu Kế toán")
        elif index == 2:
            self.lbl_phase_title.setText("✅ 3. Chốt Lớp & Phân bổ")

    def _load_academic_years(self) -> None:
        self.cb_academic_year.blockSignals(True)
        self.cb_academic_year.clear()
        years = ClassService.get_academic_years()
        if not years:
            years.append("Chưa có dữ liệu")
        self.cb_academic_year.addItems(years)
        self.cb_academic_year.blockSignals(False)
        self._load_waves_for_current_year()

    def _load_waves_for_current_year(self) -> None:
        self.cb_wave.blockSignals(True)
        self.cb_wave.clear()
        current_year = self.cb_academic_year.currentText()
        if current_year and current_year != "Chưa có dữ liệu":
            waves = ClassService.get_waves_for_year(current_year)
            if waves:
                waves = [w for w in waves if w != "Tất cả"]
            if waves:
                self.cb_wave.addItem("Tất cả")
                self.cb_wave.addItems(waves)
            else:
                self.cb_wave.addItem("Chưa có đợt")
        else:
            self.cb_wave.addItem("Chưa có đợt")
        self.cb_wave.blockSignals(False)

    def _on_year_changed(self, text: str = "") -> None:
        self._load_waves_for_current_year()
        self.load_data()

    def load_data(self, text: str = "") -> None:
        current_year = self.cb_academic_year.currentText()
        current_wave = self.cb_wave.currentText()
        is_all_waves = current_wave == "Tất cả"
        self.btn_rename_wave.setEnabled(not is_all_waves)
        self.btn_delete_wave.setEnabled(not is_all_waves)
        self.planning_tab.load_data(current_year, current_wave)
        self.is_data_loaded = True

    def create_new_year(self) -> None:
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

    def create_new_wave(self) -> None:
        current_year = self.cb_academic_year.currentText()
        if not current_year or current_year == "Chưa có dữ liệu":
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng tạo/chọn Niên khóa trước!")
            return
        wave_name, ok = QInputDialog.getText(self, "Tạo Đợt Mới", f"Nhập tên đợt mới cho {current_year}\n(VD: Đợt 2, Tháng 10...):")
        if ok and wave_name.strip():
            wave_name = ' '.join(wave_name.strip().split())
            try:
                if ClassService.create_wave_in_year(current_year, wave_name):
                    QMessageBox.information(self, "Thành công", f"Đã tạo đợt '{wave_name}' thành công!")
                    self._load_waves_for_current_year()
                    self.cb_wave.setCurrentText(wave_name)
                else:
                    QMessageBox.warning(self, "Lỗi", f"Đợt '{wave_name}' đã tồn tại!")
            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể tạo đợt mới:\n{e}")

    def rename_current_wave(self) -> None:
        current_year = self.cb_academic_year.currentText()
        current_wave = self.cb_wave.currentText()
        if not current_year or current_year == "Chưa có dữ liệu" or not current_wave or current_wave == "Chưa có đợt":
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một Đợt để sửa tên!")
            return
        if current_wave == "Tất cả":
            QMessageBox.warning(self, "Cảnh báo", "Không thể đổi tên tùy chọn 'Tất cả'!")
            return
        new_name, ok = QInputDialog.getText(self, "Đổi Tên Đợt", f"Nhập tên mới cho đợt '{current_wave}':", text=current_wave)
        if ok and new_name.strip():
            new_name = ' '.join(new_name.strip().split())
            if new_name == current_wave: return
            try:
                if ClassService.rename_wave(current_year, current_wave, new_name):
                    QMessageBox.information(self, "Thành công", f"Đã đổi tên đợt thành '{new_name}'!")
                    self._load_waves_for_current_year()
                    self.cb_wave.setCurrentText(new_name)
                else:
                    QMessageBox.warning(self, "Lỗi", f"Tên đợt '{new_name}' đã tồn tại hoặc có lỗi xảy ra.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi nghiêm trọng", f"Không thể đổi tên đợt:\n{e}")

    def delete_current_wave(self) -> None:
        current_year = self.cb_academic_year.currentText()
        current_wave = self.cb_wave.currentText()
        if not current_year or current_year == "Chưa có dữ liệu" or not current_wave or current_wave == "Chưa có đợt":
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một Đợt để xóa!")
            return
        if current_wave == "Tất cả":
            QMessageBox.warning(self, "Cảnh báo", "Không thể xóa tùy chọn 'Tất cả'!")
            return
        reply = QMessageBox.question(self, "Xác nhận xóa", f"Bạn có chắc chắn muốn XÓA vĩnh viễn đợt '{current_wave}' và TOÀN BỘ các lớp dự kiến bên trong nó không?\n\nHành động này không thể hoàn tác!", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if ClassService.delete_wave(current_year, current_wave):
                    QMessageBox.information(self, "Thành công", f"Đã xóa đợt '{current_wave}' thành công!")
                    self._load_waves_for_current_year()
                else:
                    QMessageBox.warning(self, "Không thể xóa", "Không thể xóa đợt cuối cùng trong Niên khóa, hoặc có lỗi xảy ra.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi nghiêm trọng", f"Không thể xóa đợt:\n{e}")
