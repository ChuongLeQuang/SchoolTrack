import os
import sys
import json
import time
import logging
from typing import List, Dict, Any
import re
from datetime import datetime
import requests
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
            # For packaged app, data dir is next to the executable
            project_root = os.path.dirname(sys.executable)
            data_dir = os.path.join(project_root, "data")
        else:
            # For development, it's in the source tree
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
    def get_waves_for_year(year: str) -> List[str]:
        """Lấy danh sách các Đợt từ cấu hình JSON form_links.json."""
        file_path = ClassService.get_form_links_file()
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            year_data = data.get(year, {})
            if isinstance(year_data, dict):
                return list(year_data.keys())
        except Exception:
            return []

    @staticmethod
    def get_class_codes_for_wave(year: str, wave: str) -> List[str]:
        """
        EN: Get the list of class codes associated with a specific wave from the metadata JSON.
        VI: Lấy danh sách mã lớp thuộc về một đợt cụ thể từ file JSON siêu dữ liệu.
        """
        file_path = ClassService.get_form_links_file()
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            year_data = data.get(year, {})
            wave_data = year_data.get(wave, {})
            
            if isinstance(wave_data, dict):
                return wave_data.get("classes", [])
            return []
        except Exception:
            return []

    @staticmethod
    def _parse_class_rows(raw_data: List[Dict[str, Any]]) -> List[ClassInfo]:
        """
        EN: Helper to parse raw dictionary data into a list of ClassInfo objects.
        VI: Hàm phụ trợ để chuyển đổi dữ liệu thô (dictionary) thành danh sách đối tượng ClassInfo.
        """
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
    def get_classes_from_excel(file_path: str, wave_name: str | None) -> List[ClassInfo]:
        """
        EN: Read excel file and convert it into a list of ClassInfo objects.
            If wave_name is None, read from all sheets.
        VI: Đọc file excel và chuyển thành danh sách đối tượng ClassInfo.
            Nếu wave_name là None, đọc từ tất cả các sheet.
        """
        if wave_name is not None:
            # Đọc từ một sheet cụ thể
            raw_data = ExcelService.load_excel_data(file_path, sheet_name=wave_name)
            return ClassService._parse_class_rows(raw_data)
        else:
            # Đọc từ tất cả các sheet trong file
            import openpyxl
            all_classes = []
            try:
                wb = openpyxl.load_workbook(file_path, read_only=True)
                sheet_names = wb.sheetnames
                wb.close()
                
                for sheet in sheet_names:
                    # Bỏ qua các sheet hệ thống hoặc sheet ẩn của Excel
                    if sheet.startswith("_") or "filter" in sheet.lower():
                        continue
                    raw_data = ExcelService.load_excel_data(file_path, sheet_name=sheet)
                    all_classes.extend(ClassService._parse_class_rows(raw_data))
                return all_classes
            except Exception as e:
                raise ValueError(f"Lỗi khi đọc nhiều sheet từ file {file_path}: {e}")

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
        ws.title = "Đợt 1"
        
        headers = [
            "STT", "Mã Lớp", "Niên Khóa", "Tên Lớp", "Địa điểm", "Phòng học", "Buổi học", "Lịch học", "Giờ học", 
            "Thời gian khai giảng", "Ngày kết thúc khóa", "SL Min", "SL Max", 
            "SL Hiện tại", "Trạng thái"
        ]
        ws.append(headers)
        
        wb.save(file_path)
        wb.close()
        
        # Khởi tạo siêu dữ liệu (Metadata) cho Đợt 1 vào form_links.json
        year = os.path.basename(file_path).replace("Quan Ly Lop Hoc ", "").replace(".xlsx", "")
        ClassService.save_wave_links(year, "Đợt 1", "", "")
        return True

    @staticmethod
    def create_wave_in_year(year: str, wave_name: str) -> bool:
        """Tạo một Đợt mới (Sheet mới) trong file Niên khóa."""
        file_path = ClassService.get_file_path_for_year(year)
        if not os.path.exists(file_path):
            return False
        import openpyxl
        wb = openpyxl.load_workbook(file_path)
        
        # Kiểm tra trùng lặp không phân biệt hoa thường và khoảng trắng thừa
        normalized_new_name = ' '.join(wave_name.lower().split())
        if any(' '.join(s.lower().split()) == normalized_new_name for s in wb.sheetnames):
            wb.close()
            return False
        ws = wb.create_sheet(wave_name)
        headers = ["STT", "Mã Lớp", "Niên Khóa", "Tên Lớp", "Địa điểm", "Phòng học", "Buổi học", "Lịch học", "Giờ học", "Thời gian khai giảng", "Ngày kết thúc khóa", "SL Min", "SL Max", "SL Hiện tại", "Trạng thái"]
        ws.append(headers)
        wb.save(file_path)
        wb.close()
        
        # Cập nhật siêu dữ liệu (Metadata) vào form_links.json
        ClassService.save_wave_links(year, wave_name, "", "")
        return True

    @staticmethod
    def rename_wave(year: str, old_wave_name: str, new_wave_name: str) -> bool:
        """
        EN: Rename a wave (sheet) and update the corresponding link configuration in JSON.
        VI: Đổi tên một Đợt (Sheet) và cập nhật file JSON cấu hình link tương ứng.
        """
        file_path = ClassService.get_file_path_for_year(year)
        if not os.path.exists(file_path):
            return False
        
        import openpyxl
        wb = openpyxl.load_workbook(file_path)
        if old_wave_name not in wb.sheetnames:
            wb.close()
            return False
            
        normalized_new_name = ' '.join(new_wave_name.lower().split())
        if any(' '.join(s.lower().split()) == normalized_new_name for s in wb.sheetnames if s != old_wave_name):
            wb.close()
            return False
            
        ws = wb[old_wave_name]
        ws.title = new_wave_name
        wb.save(file_path)
        wb.close()
        
        # Cập nhật file form_links.json
        links_file = ClassService.get_form_links_file()
        if os.path.exists(links_file):
            try:
                with open(links_file, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    changed = False
                    
                    # Migrate cấu trúc cũ (nếu có)
                    old_flat_key = f"{year}_{old_wave_name}"
                    if old_flat_key in data:
                        if year not in data or not isinstance(data[year], dict): data[year] = {}
                        data[year][new_wave_name] = data.pop(old_flat_key)
                        changed = True
                        
                    # Cấu trúc mới
                    if year in data and isinstance(data[year], dict) and old_wave_name in data[year]:
                        data[year][new_wave_name] = data[year].pop(old_wave_name)
                        changed = True
                        
                    if changed:
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception:
                pass # Bỏ qua nếu file JSON lỗi
        return True

    @staticmethod
    def delete_wave(year: str, wave_name: str) -> bool:
        """
        EN: Delete a wave (sheet) and update the corresponding link configuration in JSON.
        VI: Xóa một Đợt (Sheet) và cập nhật file JSON cấu hình link tương ứng.
        """
        file_path = ClassService.get_file_path_for_year(year)
        if not os.path.exists(file_path): return False
            
        import openpyxl
        wb = openpyxl.load_workbook(file_path)
        if wave_name not in wb.sheetnames or len(wb.sheetnames) <= 1:
            wb.close()
            return False
            
        wb.remove(wb[wave_name])
        wb.save(file_path)
        wb.close()
        
        # Cập nhật file form_links.json
        links_file = ClassService.get_form_links_file()
        if os.path.exists(links_file):
            try:
                with open(links_file, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    changed = False
                    
                    old_flat_key = f"{year}_{wave_name}"
                    if old_flat_key in data:
                        data.pop(old_flat_key)
                        changed = True
                        
                    if year in data and isinstance(data[year], dict) and wave_name in data[year]:
                        data[year].pop(wave_name)
                        if not data[year]: data.pop(year)
                        changed = True
                        
                    if changed:
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception:
                pass
        return True

    @staticmethod
    def save_class_to_excel(file_path: str, wave_name: str, class_info: ClassInfo) -> None:
        """
        EN: Save a ClassInfo object to the Excel file (Sheet 1).
        VI: Lưu đối tượng ClassInfo xuống file Excel theo Đợt.
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
            sheet_name=wave_name
        )
        
        # Tự động đồng bộ mã lớp vào Metadata JSON
        ClassService.update_class_in_wave_metadata(class_info.year_code, wave_name, class_info.class_code, "add")

    @staticmethod
    def update_registration_counts(file_path: str, wave_name: str, counts: Dict[str, int]) -> None:
        """
        EN: Update 'SL Hiện tại' for classes in a specific wave based on registration counts.
        VI: Cập nhật 'SL Hiện tại' cho các lớp thuộc một đợt cụ thể.
        """
        import openpyxl
        if not os.path.exists(file_path):
            return

        wb = openpyxl.load_workbook(file_path)
        updated = False
        
        # Chỉ chọn và xử lý duy nhất Sheet của Đợt hiện tại
        if wave_name in wb.sheetnames:
            sheet = wb[wave_name]
            if not (sheet.title.startswith("_") or "filter" in sheet.title.lower()):
                headers = [str(sheet.cell(row=1, column=c).value).strip().lower() if sheet.cell(row=1, column=c).value else "" for c in range(1, sheet.max_column + 1)]
                
                code_col_idx = -1
                for i, h in enumerate(headers):
                    if h in ["mã lớp", "class code", "mã"]:
                        code_col_idx = i + 1
                        break
                        
                if code_col_idx != -1:
                    count_col_idx = -1
                    for i, h in enumerate(headers):
                        if h in ["sl hiện tại", "sl now", "đăng ký"]:
                            count_col_idx = i + 1
                            break
                    if count_col_idx == -1:
                        count_col_idx = sheet.max_column + 1
                        sheet.cell(row=1, column=count_col_idx, value="SL Hiện tại")
                    
                    for row_num in range(2, sheet.max_row + 1):
                        cell_val = sheet.cell(row=row_num, column=code_col_idx).value
                        if cell_val is not None:
                            code_val = str(cell_val).strip()
                            # Cập nhật số lượng đếm được, nếu không có ai thì trả về 0 để reset số ảo cũ
                            new_count = counts.get(code_val, 0)
                            
                            current_count_val = sheet.cell(row=row_num, column=count_col_idx).value
                            try: current_count = int(current_count_val) if current_count_val is not None else 0
                            except ValueError: current_count = -1
                            
                            if current_count != new_count:
                                sheet.cell(row=row_num, column=count_col_idx, value=new_count)
                                updated = True
                        
        if updated:
            wb.save(file_path)
        wb.close()

    @staticmethod
    def delete_class_from_excel(file_path: str, year: str, wave_name: str, class_code: str) -> bool:
        """
        EN: Delete a class from the Excel file by class_code.
        VI: Xóa lớp học khỏi file Excel dựa trên Mã Lớp.
        """
        is_deleted = ExcelService.delete_row(
            file_path=file_path,
            match_cols=["Mã Lớp"],
            match_value=class_code,
            sheet_name=wave_name
        )
        if is_deleted:
            ClassService.update_class_in_wave_metadata(year, wave_name, class_code, "remove")
        return is_deleted

    @staticmethod
    def get_form_links_file() -> str:
        """Lấy đường dẫn file cấu hình lưu trữ link Google Form."""
        return os.path.join(ClassService.get_data_dir(), "form_links.json")

    @staticmethod
    def get_wave_links(year: str, wave: str) -> dict:
        """
        EN: Get the saved Google Form & Sheet links for a specific year/wave.
        VI: Lấy cặp link Google Form & Sheet đã lưu cho niên khóa/đợt cụ thể.
        """
        file_path = ClassService.get_form_links_file()
        default_links = {"form_link": "", "sheet_link": ""}
        if not os.path.exists(file_path):
            return default_links
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            year_data = data.get(year, {})
            wave_data = year_data.get(wave, {})
            
            # Hỗ trợ tương thích ngược chuẩn phẳng cũ
            old_key = f"{year}_{wave}"
            if old_key in data: wave_data = data[old_key]
                
            if isinstance(wave_data, str): return {"form_link": wave_data, "sheet_link": ""}
            elif isinstance(wave_data, dict): return {"form_link": wave_data.get("form_link", ""), "sheet_link": wave_data.get("sheet_link", "")}
            return default_links
        except Exception:
            return default_links

    @staticmethod
    def save_wave_links(year: str, wave: str, form_link: str, sheet_link: str) -> None:
        """
        EN: Save the Google Form & Sheet links mapped to a specific wave.
        """
        file_path = ClassService.get_form_links_file()
        data = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
            except Exception: pass
            
        if year not in data or not isinstance(data[year], dict): data[year] = {}
        if wave not in data[year]: data[year][wave] = {"form_link": "", "sheet_link": "", "classes": []}
            
        data[year][wave]["form_link"] = form_link
        data[year][wave]["sheet_link"] = sheet_link
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def auto_create_google_form(web_app_url: str, secret: str, template_id: str, wave_name: str, classes: List[str]) -> Dict[str, str]:
        """
        EN: Sends a request to Google Apps Script to auto-generate a Form and linked Sheet.
        VI: Gửi request lên Google Apps Script để tự động tạo Form và Sheet.
        """
        payload = {
            "secret": secret,
            "wave_name": wave_name,
            "classes": classes,
            "template_id": template_id
        }
        try:
            # allow_redirects=True rất quan trọng vì Google Scripts thường điều hướng redirect
            response = requests.post(web_app_url, json=payload, timeout=60, allow_redirects=True)
            response.raise_for_status()
            
            try:
                return response.json()
            except Exception as json_err:
                # Bắt lỗi nếu Google trả về trang HTML thay vì JSON (thường do sai quyền truy cập)
                raw_text = response.text.strip()
                if "<html" in raw_text.lower() or "<!doctype html>" in raw_text.lower():
                    return {
                        "status": "error", 
                        "message": "Google trả về trang Web (HTML) thay vì dữ liệu JSON.\n\nNguyên nhân thường gặp:\n1. Chưa chọn quyền truy cập là 'Bất kỳ ai' (Anyone) khi Deploy.\n2. URL Web App bị sai (phải kết thúc bằng /exec).\n3. Bạn copy nhầm Form ID hoặc thiếu quyền thao tác."
                    }
                return {"status": "error", "message": f"Google phản hồi sai định dạng. Dữ liệu thô:\n{raw_text[:200]}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def update_class_in_wave_metadata(year: str, wave: str, class_code: str, action: str) -> None:
        """
        EN: Add or remove a class_code from the wave metadata JSON.
        VI: Thêm hoặc xóa mã lớp khỏi cấu hình JSON của Đợt.
        """
        file_path = ClassService.get_form_links_file()
        data = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
            except Exception: pass
            
        if year not in data or not isinstance(data[year], dict): data[year] = {}
        if wave not in data[year]: data[year][wave] = {"form_link": "", "sheet_link": "", "classes": []}
        if "classes" not in data[year][wave]: data[year][wave]["classes"] = []
        
        classes = data[year][wave]["classes"]
        if action == "add" and class_code not in classes: classes.append(class_code)
        elif action == "remove" and class_code in classes: classes.remove(class_code)
            
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def download_google_sheet_as_excel(sheet_url: str, save_path: str) -> bool:
        """
        EN: Downloads a Google Sheet as an .xlsx file.
        VI: Tải một Google Sheet về dưới dạng file .xlsx.
        """
        if not sheet_url:
            return False

        # Extract Sheet ID
        id_match = re.search(r"spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
        if not id_match:
            return False
        sheet_id = id_match.group(1)

        # Tải toàn bộ file Workbook (tất cả các Sheet) thay vì chỉ tải 1 sheet mặc định
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
        
        # Thêm resourcekey nếu có trong link gốc (Google Form thường sinh ra tham số này)
        resourcekey_match = re.search(r"resourcekey=([a-zA-Z0-9-_]+)", sheet_url)
        if resourcekey_match:
            export_url += f"&resourcekey={resourcekey_match.group(1)}"

        try:
            # Cơ chế Retry (Rule 1)
            retries = 3
            for attempt in range(retries):
                try:
                    response = requests.get(export_url, stream=True, timeout=30)
                    response.raise_for_status()
                    
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' in content_type:
                        logging.error(f"[LỖI TẢI FILE]: File Google Sheet bị khóa Private. Content-Type: {content_type}")
                        return False
                        
                    with open(save_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    return True
                except requests.exceptions.RequestException as e:
                    logging.warning(f"Lỗi mạng tải file. Thử lại {attempt + 1}/{retries}... Chi tiết: {e}")
                    if attempt < retries - 1:
                        time.sleep(2)
                    else:
                        logging.error(f"[LỖI TẢI FILE]: Request thất bại sau {retries} lần thử: {e}")
                        return False
            return False
        except Exception as e:
            logging.error(f"[LỖI KHÔNG XÁC ĐỊNH]: {e}")
            return False