import os
import sys
from typing import List, Dict
from datetime import datetime
from apps.main_app.src.models.entities import ClassInfo
from apps.main_app.src.services.excel_service import ExcelService


class ClassService:
    """
    EN: Service to handle class-related business logic.
    VI: Dịch vụ xử lý nghiệp vụ liên quan đến Lớp học.
    """

    @staticmethod
    def get_data_dir() -> str:
        """
        EN: Get absolute path to the data directory, safe for PyInstaller.
        VI: Lấy đường dẫn tuyệt đối đến thư mục data, an toàn khi đóng gói PyInstaller.
        """
        if getattr(sys, 'frozen', False):
            project_root = os.path.dirname(sys.executable)
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        
        data_dir = os.path.join(project_root, "apps", "main_app", "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir

    @staticmethod
    def get_file_path_for_year(year: str) -> str:
        """
        EN: Generate Excel file path for a specific academic year.
        VI: Tạo đường dẫn file Excel cho một niên khóa cụ thể.
        """
        return os.path.join(ClassService.get_data_dir(), f"Quan Ly Lop Hoc {year}.xlsx")

    @staticmethod
    def get_academic_years() -> List[str]:
        """
        EN: Scan data directory and return a sorted list of academic years.
        VI: Quét thư mục data và trả về danh sách các niên khóa đã sắp xếp.
        """
        data_dir = ClassService.get_data_dir()
        years = []
        for file_name in os.listdir(data_dir):
            if file_name.startswith("Quan Ly Lop Hoc ") and file_name.endswith(".xlsx"):
                year = file_name.replace("Quan Ly Lop Hoc ", "").replace(".xlsx", "")
                years.append(year)
        years.sort(reverse=True)
        return years

    @staticmethod
    def get_classes_from_excel(file_path: str) -> List[ClassInfo]:
        """
        EN: Read excel file and convert it into a list of ClassInfo objects.
        VI: Đọc file excel và chuyển thành danh sách đối tượng ClassInfo.
        """
        raw_data = ExcelService.load_excel_data(file_path)
        classes = []

        def get_val(row_dict: dict, keys: list) -> str:
            row_lower = {str(k).lower(): v for k, v in row_dict.items() if k is not None}
            for key in keys:
                if key.lower() in row_lower:
                    val = row_lower[key.lower()]
                    res = str(val).strip() if val is not None else ""
                    return "" if res.lower() == "none" else res
            return ""

        for row in raw_data:
            class_code = get_val(row, ["Mã Lớp"])
            if not class_code:
                continue

            # Xử lý parse ngày kết thúc khóa
            end_date_str = get_val(row, ["Ngày kết thúc khóa", "Kết thúc"])
            end_date = None
            if end_date_str:
                end_date_clean = end_date_str.split()[0]
                try:
                    if "/" in end_date_clean:
                        end_date = datetime.strptime(end_date_clean, "%d/%m/%Y").date()
                    elif "-" in end_date_clean:
                        end_date = datetime.strptime(end_date_clean, "%Y-%m-%d").date()
                except ValueError:
                    pass

            # Xử lý ép kiểu số cho SL Min / Max (đề phòng excel chứa giá trị rỗng hoặc text)
            try: min_st = int(get_val(row, ["SL Min"]) or 0)
            except ValueError: min_st = 0
            
            try: max_st = int(get_val(row, ["SL Max"]) or 0)
            except ValueError: max_st = 0
            
            try: current_st = int(get_val(row, ["SL Hiện tại", "SL Now", "Đăng Ký"]) or 0)
            except ValueError: current_st = 0

            cls = ClassInfo(
                class_code=class_code,
                year_code=get_val(row, ["Niên Khóa"]),
                class_name=get_val(row, ["Tên Lớp"]),
                location=get_val(row, ["Địa điểm"]),
                room=get_val(row, ["Phòng học"]),
                session=get_val(row, ["Buổi học"]),
                schedule=get_val(row, ["Lịch học"]),
                time_slot=get_val(row, ["Giờ học"]),
                start_month_year=get_val(row, ["Thời gian khai giảng", "Khai giảng"]),
                end_date=end_date,
                min_students=min_st,
                max_students=max_st,
                current_students=current_st,
                class_status=get_val(row, ["Trạng thái", "Trạng Thái"]) or "Dự kiến"
            )
            classes.append(cls)

        return classes

    @staticmethod
    def create_academic_year_file(file_path: str) -> bool:
        """
        EN: Create a new Excel file for a new academic year with default headers.
        VI: Tạo file Excel mới cho một niên khóa với các tiêu đề cột chuẩn.
        """
        import openpyxl
        
        if os.path.exists(file_path):
            return False
            
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Danh Sach Lop"
        
        headers = [
            "STT", "Mã Lớp", "Niên Khóa", "Tên Lớp", "Địa điểm", "Phòng học", "Buổi học", "Lịch học", "Giờ học", 
            "Thời gian khai giảng", "Ngày kết thúc khóa", "SL Min", "SL Max", 
            "SL Hiện tại", "Trạng thái"
        ]
        ws.append(headers)
        
        wb.save(file_path)
        wb.close()
        return True

    @staticmethod
    def save_class_to_excel(file_path: str, class_info: ClassInfo) -> None:
        """
        EN: Save a ClassInfo object to the Excel file (Sheet 1).
        VI: Lưu đối tượng ClassInfo xuống file Excel (Sheet 1).
        """
        end_date_str = class_info.end_date.strftime("%d/%m/%Y") if class_info.end_date else ""

        # Khai báo mapping dữ liệu để lưu
        row_data_map = [
            (["Mã Lớp"], class_info.class_code),
            (["Niên Khóa"], class_info.year_code),
            (["Tên Lớp"], class_info.class_name),
            (["Địa điểm", "Địa Điểm"], class_info.location),
            (["Phòng học", "Phòng Học"], getattr(class_info, 'room', '')),
            (["Buổi học", "Buổi Học"], class_info.session),
            (["Lịch học", "Lịch Học"], class_info.schedule),
            (["Giờ học", "Giờ Học"], class_info.time_slot),
            (["Thời gian khai giảng", "Thời Gian"], class_info.start_month_year),
            (["Ngày kết thúc khóa", "Kết Thúc"], end_date_str),
            (["SL Min"], class_info.min_students),
            (["SL Max"], class_info.max_students),
            (["SL Hiện tại", "SL Now", "Đăng Ký"], class_info.current_students),
            (["Trạng thái", "Trạng Thái"], getattr(class_info, 'class_status', 'Dự kiến'))
        ]

        ExcelService.save_row(
            file_path=file_path,
            match_cols=["Mã Lớp"],
            match_value=class_info.class_code,
            row_data_map=row_data_map,
            sheet_name="Danh Sach Lop"
        )

    @staticmethod
    def update_registration_counts(file_path: str, counts: Dict[str, int]) -> None:
        """
        EN: Update 'SL Hiện tại' for multiple classes based on registration counts.
        VI: Cập nhật 'SL Hiện tại' cho nhiều lớp dựa trên số lượng đăng ký.
        """
        for code, count in counts.items():
            row_data_map = [(["SL Hiện tại", "SL Now", "Đăng Ký"], count)]
            ExcelService.save_row(
                file_path=file_path,
                match_cols=["Mã Lớp"],
                match_value=code,
                row_data_map=row_data_map,
                sheet_name="Danh Sach Lop"
            )

    @staticmethod
    def delete_class_from_excel(file_path: str, class_code: str) -> bool:
        """
        EN: Delete a class from the Excel file by class_code.
        VI: Xóa lớp học khỏi file Excel dựa trên Mã Lớp.
        """
        return ExcelService.delete_row(
            file_path=file_path,
            match_cols=["Mã Lớp"],
            match_value=class_code,
            sheet_name="Danh Sach Lop"
        )