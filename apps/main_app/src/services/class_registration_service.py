import re
from typing import List, Dict, Any, Tuple
from apps.main_app.src.services.core_excel_service import ExcelService
from apps.main_app.src.utils.core_text_utils import TextUtils
from apps.main_app.src.utils.core_name_matcher import NameMatcher


class RegistrationService:
    """
    EN: Service to handle student registration and sync processes.
    VI: Dịch vụ xử lý đăng ký học và đồng bộ dữ liệu kế toán.
    """

    @staticmethod
    def get_value_from_row(row: Dict[str, Any], keywords: List[str]) -> Any:
        """Tìm giá trị trong dòng dựa trên danh sách từ khóa một cách tương đối (không phân biệt hoa thường)."""
        for key, val in row.items():
            if not key:
                continue
            key_lower = str(key).lower()
            for kw in keywords:
                if kw.lower() in key_lower:
                    return val
        return None

    @staticmethod
    def extract_full_name(row: Dict[str, Any]) -> str:
        """Trích xuất Họ và Tên, hỗ trợ cả 1 cột gộp hoặc 2 cột rời."""
        full_name = RegistrationService.get_value_from_row(row, ["họ & tên", "họ tên", "họ và tên"])
        if full_name:
            return str(full_name).strip()
            
        ho = RegistrationService.get_value_from_row(row, ["họ lót", "họ đệm", "họ"])
        ten = RegistrationService.get_value_from_row(row, ["tên"])
        
        if ho or ten:
            return f"{str(ho or '').strip()} {str(ten or '').strip()}".strip()
            
        return ""

    @staticmethod
    def split_vietnamese_name(full_name: str) -> Tuple[str, str]:
        """Tách một chuỗi Họ và Tên gộp thành (Họ, Tên) để hỗ trợ lưu vào CSDL."""
        parts = str(full_name).strip().split()
        if len(parts) > 1:
            return " ".join(parts[:-1]), parts[-1]
        return "", str(full_name).strip()

    @staticmethod
    def extract_class_code(text: str) -> str:
        """Trích xuất Mã lớp từ chuỗi Google Form bằng Regex."""
        if not text:
            return ""
        match = re.search(r"\[mã:\s*([A-Za-z0-9_]+)\]", str(text), re.IGNORECASE)
        if match:
            return match.group(1).strip().upper()
        return ""

    @staticmethod
    def parse_accounting_file(file_path: str) -> List[Dict[str, Any]]:
        raw_data = ExcelService.load_excel_data(file_path)
        results = []
        
        for row in raw_data:
            student_id = RegistrationService.get_value_from_row(row, ["mã sinh viên", "mã sv", "msv"])
            full_name = RegistrationService.get_value_from_row(row, ["họ & tên", "họ tên", "họ và tên"])
            contact_info = RegistrationService.get_value_from_row(row, ["email", "số điện thoại", "phone", "sđt"])
            
            class_selection = None
            for key, val in row.items():
                if val and "[mã:" in str(val).lower():
                    class_selection = str(val)
                    break

            if not student_id or not class_selection:
                continue
                
            results.append({
                "student_id": str(student_id).strip(),
                "full_name": str(full_name).strip() if full_name else "",
                "contact_info": str(contact_info).strip() if contact_info else "",
                "class_code": RegistrationService.extract_class_code(class_selection)
            })
            
        return results

    @staticmethod
    def count_registrations_from_file(file_path: str, mode: int = 1, students_db: List[Any] = None) -> Tuple[Dict[str, int], List[str]]:
        """
        EN: Count registrations from Google Form excel file, keeping only the latest entry per student.
        VI: Đếm số lượng đăng ký từ file Excel của Google Form, chỉ giữ lại lượt nộp mới nhất của mỗi sinh viên (dựa trên MSV).
        Returns a tuple: (counts_dict, warnings_list)
        """
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True)
            sheet_names = wb.sheetnames
            wb.close()
            
            raw_data = []
            # Duyệt qua các sheet, tìm sheet đầu tiên có chứa dữ liệu (tránh sheet trống)
            for sheet in sheet_names:
                data = ExcelService.load_excel_data(file_path, sheet_name=sheet)
                if data:
                    raw_data = data
                    break
                    
        except Exception as e:
            # EN: Catch file reading errors
            # VI: Bắt lỗi không thể đọc file Excel
            raise ValueError(f"Không thể đọc file dữ liệu: {e}")

        latest_registrations: Dict[str, str] = {}
        warnings: List[str] = []
        
        # Tạo bộ từ điển (hash maps) để tra cứu nhanh sinh viên
        valid_msv = {}
        email_map = {}
        phone_map = {}
        name_map = {}
        
        if students_db:
            for s in students_db:
                msv_upper = str(s.student_id).strip().upper()
                valid_msv[msv_upper] = s
                if getattr(s, 'email', None):
                    email_map[str(s.email).strip().lower()] = msv_upper
                if getattr(s, 'phone_number', None):
                    # Dùng Regex loại bỏ mọi ký tự không phải số để so sánh SĐT cho chuẩn
                    clean_phone = re.sub(r'\D', '', str(s.phone_number))
                    phone_map[clean_phone] = msv_upper
                if getattr(s, 'full_name', None):
                    # Đưa tên trong Danh sách gốc qua "Máy mài" không dấu
                    clean_name = TextUtils.normalize_vietnamese(s.full_name)
                    name_map[clean_name] = msv_upper
        
        for idx, row in enumerate(raw_data):
            # 1. Trích xuất MSV và Tên
            student_id = RegistrationService.get_value_from_row(row, ["mã sinh viên", "mã sv", "msv"])
            if student_id:
                student_id = str(student_id).strip()
                if student_id.endswith(".0"):
                    student_id = student_id[:-2]
            full_name = RegistrationService.extract_full_name(row) or "Không rõ tên"
            
            student_key = str(student_id).strip().upper() if student_id else ""
            
            # BƯỚC ĐỐI CHIẾU & SỬA LỖI (Dựa trên students_db và mode)
            if students_db is not None:
                if not student_key or student_key not in valid_msv:
                    resolved = False
                    if mode == 3: # Chế độ thông minh: Cố gắng tự sửa
                        contact_info = str(RegistrationService.get_value_from_row(row, ["email", "số điện thoại", "phone", "sđt"]) or "")
                        row_email = contact_info.strip().lower()
                        phone_clean = contact_info.strip()
                        if phone_clean.endswith(".0"): phone_clean = phone_clean[:-2]
                        row_phone = re.sub(r'\D', '', phone_clean)
                        # Đưa tên người nộp Form qua "Máy mài" không dấu
                        row_name = TextUtils.normalize_vietnamese(full_name)
                        
                        if row_email and row_email in email_map:
                            student_key = email_map[row_email]
                            resolved = True
                        elif row_phone and row_phone in phone_map:
                            student_key = phone_map[row_phone]
                            resolved = True
                        elif row_name and row_name in name_map:
                            student_key = name_map[row_name]
                            resolved = True
                            
                    if not resolved:
                        if mode in [2, 3]: # Chế độ Cảnh báo hoặc Thông minh (nhưng sửa không được)
                            warnings.append(f"- SV '{full_name}' nhập sai MSV: '{student_id or 'Trống'}'")
                        continue # Lọc cứng: Luôn luôn bỏ qua nếu MSV vẫn không hợp lệ
                        
                # BỘ LỌC KÉP: Xác thực danh tính để quyết định có cho phép Đăng ký Lớp học không
                if student_key and student_key in valid_msv:
                    db_student = valid_msv[student_key]
                    
                    is_match, match_type, score = NameMatcher.compare_names_hybrid(full_name, db_student.full_name)
                    
                    if is_match:
                        pass # Được phép đăng ký
                    else:
                        warnings.append(f"- Từ chối SV '{full_name}' do tên không khớp hồ sơ gốc '{db_student.full_name}' (Độ khớp: {score*100:.1f}%, MSV: {student_key})")
                        continue # Khóa, từ chối toàn bộ đăng ký
            else:
                if not student_key: student_key = f"UNKNOWN_STUDENT_{idx}"
            
            # 2. Tìm cột chứa thông tin chọn lớp học
            class_selection = None
            for key, val in row.items():
                if val and "[mã:" in str(val).lower():
                    class_selection = str(val)
                    break
                    
            if not class_selection:
                continue
                
            code = RegistrationService.extract_class_code(class_selection)
            if code:
                # 3. Lõi thuật toán: Ghi đè (Overwrite) thông tin đăng ký theo student_key
                latest_registrations[student_key] = code
                
        # 4. Gom nhóm và đếm tổng số lượng đăng ký hợp lệ cho từng mã lớp
        counts: Dict[str, int] = {}
        for msv, code in latest_registrations.items():
            counts[code] = counts.get(code, 0) + 1
                
        return counts, warnings