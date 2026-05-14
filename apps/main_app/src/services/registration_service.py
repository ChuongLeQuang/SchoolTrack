import re
from typing import List, Dict, Any, Tuple
from apps.main_app.src.services.excel_service import ExcelService


class RegistrationService:
    """
    EN: Service to handle student registration and sync processes.
    VI: Dịch vụ xử lý đăng ký học và đồng bộ dữ liệu kế toán.
    """

    @staticmethod
    def extract_class_code(text: str) -> str:
        """Trích xuất Mã lớp từ chuỗi Google Form bằng Regex."""
        if not text:
            return ""
        match = re.search(r"\[Mã:\s*([A-Za-z0-9]+)\]", str(text))
        if match:
            return match.group(1).strip()
        return ""

    @staticmethod
    def parse_accounting_file(file_path: str) -> List[Dict[str, Any]]:
        raw_data = ExcelService.load_excel_data(file_path)
        results = []
        
        for row in raw_data:
            student_id = row.get("Mã Sinh viên") or row.get("Mã SV")
            full_name = row.get("Họ & Tên") or row.get("Họ tên") or row.get("Họ và tên")
            contact_info = row.get("Email hay Phone") or row.get("Email")
            
            class_selection = None
            for key, val in row.items():
                if val and "[Mã:" in str(val):
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
            raw_data = ExcelService.load_excel_data(file_path)
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
        
        for idx, row in enumerate(raw_data):
            # 1. Trích xuất MSV (Hỗ trợ nhiều biến thể tên cột)
            student_id = row.get("Mã Sinh viên") or row.get("Mã SV") or row.get("MSV") or row.get("Mã Sinh Viên")
            full_name = row.get("Họ & Tên") or row.get("Họ tên") or row.get("Họ và tên") or "Không rõ tên"
            
            student_key = str(student_id).strip().upper() if student_id else ""
            
            # BƯỚC ĐỐI CHIẾU & SỬA LỖI (Dựa trên students_db và mode)
            if students_db is not None:
                if not student_key or student_key not in valid_msv:
                    resolved = False
                    if mode == 3: # Chế độ thông minh: Cố gắng tự sửa
                        row_email = str(row.get("Email hay Phone") or row.get("Email") or "").strip().lower()
                        row_phone = re.sub(r'\D', '', str(row.get("Số điện thoại") or row.get("Phone") or row.get("Email hay Phone") or ""))
                        
                        if row_email and row_email in email_map:
                            student_key = email_map[row_email]
                            resolved = True
                        elif row_phone and row_phone in phone_map:
                            student_key = phone_map[row_phone]
                            resolved = True
                            
                    if not resolved:
                        if mode in [2, 3]: # Chế độ Cảnh báo hoặc Thông minh (nhưng sửa không được)
                            warnings.append(f"- SV '{full_name}' nhập sai MSV: '{student_id or 'Trống'}'")
                        continue # Lọc cứng: Luôn luôn bỏ qua nếu MSV vẫn không hợp lệ
            else:
                if not student_key: student_key = f"UNKNOWN_STUDENT_{idx}"
            
            # 2. Tìm cột chứa thông tin chọn lớp học
            class_selection = None
            for key, val in row.items():
                if val and "[Mã:" in str(val):
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