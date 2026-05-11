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
            class_selection = row.get("Bạn muốn đăng ký học lớp nào") or row.get("Lớp đăng ký")
            
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
        """Đếm số lượng sinh viên đăng ký cho từng mã lớp từ file Google Form."""
        raw_data = ExcelService.load_excel_data(file_path)
        counts = {}
        
        for row in raw_data:
            class_selection = row.get("Bạn muốn đăng ký học lớp nào") or row.get("Lớp đăng ký")
            if not class_selection:
                continue
            code = RegistrationService.extract_class_code(class_selection)
            if code:
                counts[code] = counts.get(code, 0) + 1
                
        return counts