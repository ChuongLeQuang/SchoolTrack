from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QStackedWidget
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QCloseEvent, QPixmap
import os
import sys
from apps.main_app.src.views.student_view import StudentView
from apps.main_app.src.views.class_view import ClassView


class MainWindow(QMainWindow):
    """
    EN: Main Dashboard Window for SchoolTrack.
    VI: Cửa sổ giao diện chính (Dashboard) của SchoolTrack.
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SchoolTrack - Quản lý Lớp học")
        
        # Thiết lập QSettings và Khôi phục kích thước cửa sổ
        self.settings = QSettings("SchoolTrackOrg", "SchoolTrack")
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1024, 768)
            
        self._setup_ui()
        self.content_stack.currentChanged.connect(self.on_screen_changed)

    def _setup_ui(self) -> None:
        """
        EN: Setup user interface layout and components.
        VI: Khởi tạo các thành phần layout và giao diện.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout (Horizontal: Sidebar + Content)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Setup
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setFrameShadow(QFrame.Shadow.Raised)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)

        # App Title in Sidebar
        app_title = QLabel("SchoolTrack")
        app_title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_title)

        # Navigation Buttons
        btn_dashboard = QPushButton("📊  Dashboard")
        btn_students = QPushButton("🧑‍🎓  Quản lý Sinh viên")
        btn_classes = QPushButton("🏫  Quản lý Lớp học")
        btn_registration = QPushButton("📝  Đăng ký Lớp")

        # Style for buttons
        button_style = """
            QPushButton { 
                padding: 10px 15px; text-align: left; font-size: 16px; font-weight: bold;
            }
        """
        for btn in [btn_dashboard, btn_students, btn_classes, btn_registration]:
            btn.setStyleSheet(button_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            sidebar_layout.addWidget(btn)

            if btn == btn_classes:
                # Sub-menu cho Quản lý Lớp học (Accordion)
                self.sub_menu_classes = QWidget()
                sub_layout = QVBoxLayout()
                sub_layout.setContentsMargins(0, 0, 0, 0)
                sub_layout.setSpacing(5)
                
                self.btn_sub_plan = QPushButton("📝  1. Kế hoạch Dự kiến")
                self.btn_sub_sync = QPushButton("💰  2. Đối chiếu Kế toán")
                self.btn_sub_final = QPushButton("✅  3. Chốt Lớp & Phân bổ")
                
                sub_button_style = """
                    QPushButton { 
                        padding: 8px 15px 8px 45px; text-align: left; font-size: 14px;
                        border: none; background-color: transparent; color: #4B5563;
                    }
                    QPushButton:hover { background-color: #E5E7EB; border-radius: 4px; color: #1F2937; font-weight: bold;}
                """
                for sub_btn in [self.btn_sub_plan, self.btn_sub_sync, self.btn_sub_final]:
                    sub_btn.setStyleSheet(sub_button_style)
                    sub_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    sub_layout.addWidget(sub_btn)
                    
                self.sub_menu_classes.setLayout(sub_layout)
                self.sub_menu_classes.setVisible(False)
                sidebar_layout.addWidget(self.sub_menu_classes)

        sidebar_layout.addStretch()  # Push everything up
        
        # Thêm logo bản quyền ở dưới cùng Sidebar
        lbl_logo = QLabel()
        if getattr(sys, 'frozen', False):
            project_root = sys._MEIPASS
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

        logo_path = os.path.join(project_root, "assets", "2CJ1_3D.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            lbl_logo.setPixmap(pixmap.scaledToWidth(120, Qt.TransformationMode.SmoothTransformation))
            lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_logo.setToolTip("Copyright (c) 2026 Le Quang Chuong")
        sidebar_layout.addWidget(lbl_logo)

        sidebar.setLayout(sidebar_layout)

        # 2. Main Content Setup
        content_area = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Use QStackedWidget to manage multiple screens
        self.content_stack = QStackedWidget()
        
        # --- Screen 0: Dashboard Placeholder ---
        self.dashboard_view = QWidget()
        dash_layout = QVBoxLayout()
        content_title = QLabel("📊 Khu vực Tổng quan (Dashboard)")
        content_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        dash_layout.addWidget(content_title)
        self.dashboard_view.setLayout(dash_layout)
        
        # --- Screen 1: Student Management View ---
        self.student_view = StudentView()
        
        # --- Screen 2: Class Management View ---
        self.class_view = ClassView()
        
        # Add screens to stack
        self.content_stack.addWidget(self.dashboard_view)  # Index 0
        self.content_stack.addWidget(self.student_view)    # Index 1
        self.content_stack.addWidget(self.class_view)      # Index 2
        
        content_layout.addWidget(self.content_stack)
        
        content_area.setLayout(content_layout)

        # Add to Main Layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)

        central_widget.setLayout(main_layout)

        # --- Connect Sidebar Buttons to Stacked Widget ---
        btn_dashboard.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        btn_students.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        
        # Logic ẩn/hiện menu Lớp học
        def toggle_class_menu():
            is_visible = self.sub_menu_classes.isVisible()
            self.sub_menu_classes.setVisible(not is_visible)
            self.content_stack.setCurrentIndex(2)
            if not is_visible:
                self.class_view.set_active_screen(0) # Mở tab 1 mặc định
                
        btn_classes.clicked.connect(toggle_class_menu)
        
        self.btn_sub_plan.clicked.connect(lambda: [self.content_stack.setCurrentIndex(2), self.class_view.set_active_screen(0)])
        self.btn_sub_sync.clicked.connect(lambda: [self.content_stack.setCurrentIndex(2), self.class_view.set_active_screen(1)])
        self.btn_sub_final.clicked.connect(lambda: [self.content_stack.setCurrentIndex(2), self.class_view.set_active_screen(2)])

    def on_screen_changed(self, index: int) -> None:
        """
        EN: Load data for a view only when it becomes active for the first time.
        VI: Chỉ tải dữ liệu cho một màn hình khi nó được kích hoạt lần đầu tiên.
        """
        if index == 1: # Student View
            if not self.student_view.is_data_loaded:
                self.student_view.load_data()
        elif index == 2: # Class View
            if not self.class_view.is_data_loaded:
                self.class_view.load_data()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        EN: Save window size and position before closing.
        VI: Lưu lại kích thước và vị trí cửa sổ trước khi đóng.
        """
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)