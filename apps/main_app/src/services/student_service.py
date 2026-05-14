import os
import sys
from typing import List
from datetime import datetime, date
from apps.main_app.src.models.entities import Student
from apps.main_app.src.services.excel_service import ExcelService


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
    def get_students_from_excel(file_path: str) -> List[Student]:
        """
        EN: Read excel file and convert it into a list of Student objects.
        VI: Đọc file excel và chuyển thành danh sách đối tượng Student.
        """
        raw_data = ExcelService.load_excel_data(file_path)
        students = []

        for row in raw_data:
            # Tìm MSV linh hoạt hơn với các biến thể tên cột
            student_id = row.get("Mã Sinh viên") or row.get("Mã SV") or row.get("MSV") or row.get("Mã Sinh Viên")
            if not student_id:
                continue

            # Xử lý parse ngày sinh (hỗ trợ định dạng ISO hoặc DD/MM/YYYY)
            dob_str = row.get("Ngày sinh") or row.get("DOB") or row.get("Ngày Sinh")
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
                balance_str = row.get("Số dư học phí") or row.get("Số dư") or row.get("Học phí") or "0"
                balance_raw = str(balance_str).replace(",", "").replace(".", "").strip()
                tuition_balance = int(balance_raw)
            except ValueError:
                tuition_balance = 0

            # Xử lý Họ và Tên (Hỗ trợ file có 1 cột gộp hoặc 2 cột tách rời)
            full_name = row.get("Họ và tên") or row.get("Họ Tên") or row.get("Họ tên")
            if not full_name:
                ho = str(row.get("Họ") or row.get("Họ lót") or "").strip()
                ten = str(row.get("Tên") or "").strip()
                full_name = f"{ho} {ten}".strip()

            # Tạo đối tượng Student
            student = Student(
                student_id=str(student_id).strip(),
                full_name=full_name,
                date_of_birth=dob,
                email=str(row.get("Email") or "").strip(),
                phone_number=str(row.get("Số điện thoại") or row.get("SĐT") or row.get("Điện thoại") or "").strip(),
                study_status=str(row.get("Trạng thái học tập") or row.get("Trạng thái") or "Đang học").strip(),
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