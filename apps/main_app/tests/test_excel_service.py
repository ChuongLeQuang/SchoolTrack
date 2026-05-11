import os
import openpyxl
import pytest
from apps.main_app.src.services.excel_service import ExcelService


def test_load_excel_data_file_not_found():
    """
    EN: Test reading a non-existent Excel file raises FileNotFoundError.
    VI: Kiểm thử đọc file Excel không tồn tại sẽ văng lỗi FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        ExcelService.load_excel_data("non_existent_file_abc.xlsx")


def test_load_excel_data_success(tmp_path):
    """
    EN: Test successfully reading an Excel file.
    VI: Kiểm thử đọc file Excel thành công với dữ liệu mẫu.
    """
    # Tạo file Excel giả lập (mock) trong thư mục tạm
    mock_file_path = os.path.join(tmp_path, "mock_data.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["MSV", "HoTen"])
    ws.append(["SV01", "Nguyen Van A"])
    ws.append(["SV02", "Tran Thi B"])
    wb.save(mock_file_path)

    # Gọi service để test
    data = ExcelService.load_excel_data(mock_file_path)
    
    # Assertions
    assert len(data) == 2
    assert data[0]["MSV"] == "SV01"
    assert data[1]["HoTen"] == "Tran Thi B"