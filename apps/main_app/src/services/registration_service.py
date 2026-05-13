import re
from typing import List, Dict, Any
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
    def count_registrations_from_file(file_path: str) -> Dict[str, int]:
        """
        EN: Count registrations from Google Form excel file, keeping only the latest entry per student.
        VI: Đếm số lượng đăng ký từ file Excel của Google Form, chỉ giữ lại lượt nộp mới nhất của mỗi sinh viên (dựa trên MSV).
        """
        try:
            raw_data = ExcelService.load_excel_data(file_path)
        except Exception as e:
            # EN: Catch file reading errors
            # VI: Bắt lỗi không thể đọc file Excel
            raise ValueError(f"Không thể đọc file dữ liệu: {e}")

        latest_registrations: Dict[str, str] = {}
        
        for idx, row in enumerate(raw_data):
            # 1. Trích xuất MSV (Hỗ trợ nhiều biến thể tên cột)
            student_id = row.get("Mã Sinh viên") or row.get("Mã SV") or row.get("MSV") or row.get("Mã Sinh Viên")
            
            # Nếu sinh viên không nhập MSV, dùng chỉ số dòng làm key tạm để không bị bỏ sót
            student_key = str(student_id).strip().upper() if student_id else f"UNKNOWN_STUDENT_{idx}"
            
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
                
        return counts