import os
import sys
import json
import re
from typing import List, Any, Dict
from datetime import datetime, date
from apps.main_app.src.models.entities import Student
from apps.main_app.src.services.core_excel_service import ExcelService


class StudentService:
    """
    EN: Service to handle student-related business logic.
    VI: Dịch vụ xử lý nghiệp vụ liên quan đến Sinh viên.
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
    def get_file_path() -> str:
        return os.path.join(StudentService.get_data_dir(), "Danh Sach SV.xlsx")

    @staticmethod
    def get_pending_updates_file() -> str:
        return os.path.join(StudentService.get_data_dir(), "pending_updates.json")

    @staticmethod
    def save_pending_updates(updates: List[Dict[str, str]]) -> None:
        file_path = StudentService.get_pending_updates_file()
        existing = []
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f: existing = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError): 
                # EN: Safe fallback if pending_updates file is missing or corrupted.
                # VI: Bỏ qua an toàn nếu file JSON cập nhật đang chờ bị thiếu hoặc lỗi cấu trúc.
                pass
        
        for u in updates:
            if not any(e["msv"] == u["msv"] and e["type"] == u["type"] and e["new_val"] == u["new_val"] for e in existing):
                existing.append(u)
                
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4, ensure_ascii=False)

    @staticmethod
    def scan_form_for_enrichment(file_path: str, students_db: List[Student]) -> int:
        """
        EN: Scan Google Form for new info and generate pending updates.
        VI: Quét Google Form để tìm thông tin mới và tạo danh sách chờ duyệt.
        Returns the number of new updates found.
        """
        import openpyxl
        from apps.main_app.src.utils.core_name_matcher import NameMatcher
        
        wb = openpyxl.load_workbook(file_path, read_only=True)
        sheet_names = wb.sheetnames
        wb.close()
        
        raw_data = []
        for sheet in sheet_names:
            data = ExcelService.load_excel_data(file_path, sheet_name=sheet)
            if data:
                raw_data = data
                break
                
        valid_msv = {str(s.student_id).strip().upper(): s for s in students_db}
        
        def get_val(row_dict: dict, keys: list) -> Any:
            for k, v in row_dict.items():
                if not k: continue
                k_lower = str(k).lower()
                for key in keys:
                    if key.lower() in k_lower: return v
            return None
            
        pending_updates = []
        for row in raw_data:
            student_id = get_val(row, ["mã sinh viên", "mã sv", "msv"])
            if student_id:
                student_id = str(student_id).strip()
                if student_id.endswith(".0"): student_id = student_id[:-2]
            
            full_name = get_val(row, ["họ & tên", "họ tên", "họ và tên"]) or "Không rõ tên"
            student_key = str(student_id).strip().upper() if student_id else ""
            
            if student_key and student_key in valid_msv:
                db_student = valid_msv[student_key]
                is_match, match_type, score = NameMatcher.compare_names_hybrid(full_name, db_student.full_name)
                
                if is_match:
                    if match_type == "V2_MATCH" and full_name != db_student.full_name:
                        pending_updates.append({"msv": student_key, "type": "Tên", "old_val": db_student.full_name, "new_val": full_name})
                        
                    row_phone_raw = str(get_val(row, ["số điện thoại", "phone", "sđt"]) or "").strip()
                    if row_phone_raw.endswith(".0"): row_phone_raw = row_phone_raw[:-2]
                    row_phone = re.sub(r'\D', '', row_phone_raw)
                    if row_phone and len(row_phone) >= 9:
                        db_phones = [re.sub(r'\D', '', p) for p in str(db_student.phone_number).split(",")]
                        if row_phone not in db_phones:
                            pending_updates.append({"msv": student_key, "type": "SĐT", "old_val": str(db_student.phone_number), "new_val": row_phone_raw})
                            
                    row_email = str(get_val(row, ["email"]) or "").strip()
                    if row_email and "@" in row_email and "." in row_email:
                        db_emails = [e.strip().lower() for e in str(db_student.email).split(",")]
                        if row_email.lower() not in db_emails:
                            pending_updates.append({"msv": student_key, "type": "Email", "old_val": str(db_student.email), "new_val": row_email})
                            
        if pending_updates:
            StudentService.save_pending_updates(pending_updates)
        return len(pending_updates)

    @staticmethod
    def get_students_from_excel(file_path: str) -> List[Student]:
        """
        EN: Read excel file and convert it into a list of Student objects.
        VI: Đọc file excel và chuyển thành danh sách đối tượng Student.
        """
        raw_data = ExcelService.load_excel_data(file_path)
        students = []

        def get_val(row_dict: dict, keys: list) -> Any:
            for k, v in row_dict.items():
                if not k: continue
                k_lower = str(k).lower()
                for key in keys:
                    if key.lower() in k_lower:
                        return v
            return None

        for row in raw_data:
            # Tìm MSV linh hoạt hơn với các biến thể tên cột
            student_id = get_val(row, ["mã sinh viên", "mã sv", "msv"])
            if student_id:
                student_id = str(student_id).strip()
                if student_id.endswith(".0"):
                    student_id = student_id[:-2]
                    
            if not student_id:
                continue

            # Xử lý parse ngày sinh (hỗ trợ định dạng ISO hoặc DD/MM/YYYY)
            dob_str = get_val(row, ["ngày sinh", "dob"])
            dob = None
            if dob_str:
                dob_str_clean = str(dob_str).strip().split()[0]  # Lấy phần ngày, bỏ phần giờ nếu có
                try:
                    if "/" in dob_str_clean:
                        dob = datetime.strptime(dob_str_clean, "%d/%m/%Y").date()
                    elif "-" in dob_str_clean:
                        dob = datetime.strptime(dob_str_clean, "%Y-%m-%d").date()
                except ValueError:
                    pass  # Nếu lỗi parse ngày, gán None

            # Xử lý số dư học phí (loại bỏ dấu phẩy/chấm nếu có)
            try:
                balance_str = get_val(row, ["số dư học phí", "số dư", "học phí"]) or "0"
                balance_raw = str(balance_str).replace(",", "").replace(".", "").strip()
                tuition_balance = int(balance_raw)
            except ValueError:
                tuition_balance = 0

            # Xử lý Họ và Tên (Hỗ trợ file có 1 cột gộp hoặc 2 cột tách rời)
            full_name = get_val(row, ["họ & tên", "họ tên", "họ và tên"])
            if not full_name:
                ho = str(get_val(row, ["họ lót", "họ đệm", "họ"]) or "").strip()
                ten = str(get_val(row, ["tên"]) or "").strip()
                full_name = f"{ho} {ten}".strip()

            # Xử lý Email (Hỗ trợ danh sách email cách nhau bằng dấu phẩy)
            email_raw = str(get_val(row, ["email"]) or "").strip()
            emails = [e.strip() for e in email_raw.split(",") if e.strip()]
            email_val = ", ".join(emails)

            # Xử lý Số điện thoại (Hỗ trợ danh sách SĐT cách nhau bằng dấu phẩy, chống lỗi ép kiểu số của Excel)
            phone_val_raw = str(get_val(row, ["số điện thoại", "sđt", "điện thoại", "phone"]) or "").strip()
            phones = []
            for p in phone_val_raw.split(","):
                p = p.strip()
                if p.endswith(".0"): p = p[:-2]
                if p and not p.startswith("0") and p.isdigit(): p = "0" + p
                if p: phones.append(p)
            phone_val = ", ".join(phones)

            # Tạo đối tượng Student
            student = Student(
                student_id=str(student_id).strip(),
                full_name=full_name,
                date_of_birth=dob,
                email=email_val,
                phone_number=phone_val,
                study_status=str(get_val(row, ["trạng thái học tập", "trạng thái"]) or "Đang học").strip(),
                tuition_balance=tuition_balance
            )
            students.append(student)

        return students

    @staticmethod
    def save_student_to_excel(file_path: str, student: Student) -> None:
        """
        EN: Save a Student object to Excel.
        VI: Lưu đối tượng Sinh viên vào file Excel.
        """
        # Convert student dob to string formatting DD/MM/YYYY
        dob_str = student.date_of_birth.strftime("%d/%m/%Y") if student.date_of_birth else ""
        
        # Tách Họ và Tên từ full_name
        name_parts = student.full_name.strip().split()
        if len(name_parts) > 1:
            ho = " ".join(name_parts[:-1])
            ten = name_parts[-1]
        else:
            ho = ""
            ten = student.full_name.strip()
        
        row_data_map = [
            (["Mã Sinh viên", "Mã SV", "MSV", "Mã Sinh Viên"], student.student_id),
            (["Họ và tên", "Họ Tên", "Họ tên"], student.full_name),
            (["Họ", "Họ lót"], ho),
            (["Tên"], ten),
            (["Ngày sinh", "DOB", "Ngày Sinh"], dob_str),
            (["Email"], student.email),
            (["Số điện thoại", "SĐT", "Điện thoại", "Phone"], student.phone_number),
            (["Trạng thái học tập", "Trạng thái"], student.study_status),
            (["Số dư học phí", "Số dư", "Học phí"], student.tuition_balance)
        ]
        
        match_cols = ["Mã Sinh viên", "Mã SV", "MSV", "Mã Sinh Viên"]
        ExcelService.save_row(file_path, match_cols, student.student_id, row_data_map)

    @staticmethod
    def delete_student_from_excel(file_path: str, student_id: str) -> bool:
        """
        EN: Delete a student from Excel by ID.
        VI: Xóa sinh viên khỏi file Excel dựa trên Mã SV.
        """
        match_cols = ["Mã Sinh viên", "Mã SV", "MSV", "Mã Sinh Viên"]
        return ExcelService.delete_row(file_path, match_cols, student_id)