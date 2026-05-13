import pytest
from unittest.mock import patch
from apps.main_app.src.services.registration_service import RegistrationService


@patch("apps.main_app.src.services.excel_service.ExcelService.load_excel_data")
def test_parse_accounting_file(mock_load_excel) -> None:
    """
    EN: Test parsing Google Form/Accounting Excel file.
    VI: Kiểm thử việc đọc và bóc tách dữ liệu từ file Excel Kế toán/Google Form.
    """
    mock_load_excel.return_value = [
        {
            "Timestamp": "11/05/2026 12:27:30",
            "Mã Sinh viên": "25807500161",
            "Họ & Tên": "Nguyễn Phương Uyên",
            "Email hay Phone": "ngphuonguyen@gmail.com",
            "Bạn muốn đăng ký học lớp nào": "Tiếng Anh Level 2 - Tối 2-4-6 (18:00 - 20:00) - Cơ sở Bình Thạnh [Mã: LNH0526NDB]"
        }
    ]

    results = RegistrationService.parse_accounting_file("dummy_path.xlsx")
    
    assert len(results) == 1
    assert results[0]["student_id"] == "25807500161"
    assert results[0]["full_name"] == "Nguyễn Phương Uyên"
    assert results[0]["contact_info"] == "ngphuonguyen@gmail.com"
    assert results[0]["class_code"] == "LNH0526NDB"  # Bóc tách thành công mã lớp


def test_extract_class_code() -> None:
    """
    EN: Test extracting class code from a string using Regex.
    VI: Kiểm thử việc trích xuất mã lớp từ chuỗi sử dụng Regex.
    """
    text = "Tiếng Anh Level 1 - Tối 2-4-6 (18:00 - 20:00) - Cơ sở Q9 [Mã: LNH0526NEA]"
    assert RegistrationService.extract_class_code(text) == "LNH0526NEA"
    
    assert RegistrationService.extract_class_code("Không có mã ở đây") == ""


@patch("apps.main_app.src.services.excel_service.ExcelService.load_excel_data")
def test_count_registrations_from_file(mock_load_excel) -> None:
    """
    EN: Test counting registrations from an Excel file data map.
    VI: Kiểm thử việc đếm số lượng đăng ký từ dữ liệu file Excel.
    """
    mock_load_excel.return_value = [
        {"Cột bất kỳ": "Tiếng Anh Level 2 - Tối [Mã: LNH0526NDB]"},
        {"Chọn lớp": "Tiếng Anh Level 1 - Tối [Mã: LNH0526NEA]"},
        {"Lớp đăng ký": "Tiếng Anh Level 1 - Tối [Mã: LNH0526NEA]"},
        {"Cột khác": "Không có mã"}
    ]
    
    counts = RegistrationService.count_registrations_from_file("dummy.xlsx")
    
    assert len(counts) == 2
    assert counts["LNH0526NEA"] == 2
    assert counts["LNH0526NDB"] == 1