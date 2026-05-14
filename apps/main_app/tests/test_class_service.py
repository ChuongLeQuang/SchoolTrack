import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from apps.main_app.src.models.entities import ClassInfo
from apps.main_app.src.services.class_service import ClassService


@patch("apps.main_app.src.services.excel_service.ExcelService.load_excel_data")
def test_get_classes_from_excel(mock_load_excel) -> None:
    """
    EN: Test parsing raw Excel dictionary to ClassInfo objects.
    VI: Kiểm thử chuyển đổi dữ liệu Excel (dict) thành đối tượng ClassInfo.
    """
    mock_load_excel.return_value = [
        {
            "Mã Lớp": "LNH08202501",
            "Tên Lớp": "Toán Cơ Bản",
            "Niên Khóa": "2025-2026",
            "Địa điểm": "Cơ sở Q9",
            "Phòng học": "Phòng 101",
            "Buổi Học": "Sáng",
            "Lịch Học": "2-4-6",
            "Giờ Học": "08:00 - 10:00",
            "Thời gian khai giảng": "08/2025",
            "Ngày kết thúc khóa": "31/12/2025",
            "SL Min": "10",
            "SL Max": "30",
            "SL Hiện tại": "5",
            "Trạng thái": "Đang mở"
        }
    ]
    
    classes = ClassService.get_classes_from_excel("fake_path.xlsx", "Đợt 1")
    
    assert len(classes) == 1
    assert classes[0].class_code == "LNH08202501"
    assert classes[0].class_name == "Toán Cơ Bản"
    assert classes[0].location == "Cơ sở Q9"
    assert getattr(classes[0], 'room', '') == "Phòng 101"
    assert getattr(classes[0], 'session', '') == "Sáng"
    assert getattr(classes[0], 'schedule', '') == "2-4-6"
    assert getattr(classes[0], 'time_slot', '') == "08:00 - 10:00"
    assert classes[0].min_students == 10
    assert classes[0].max_students == 30
    assert classes[0].current_students == 5
    assert getattr(classes[0], 'class_status', '') == "Đang mở"
    assert classes[0].end_date == date(2025, 12, 31)

@patch("openpyxl.load_workbook")
@patch("apps.main_app.src.services.excel_service.ExcelService.load_excel_data")
def test_get_classes_from_excel_all_sheets(mock_load_excel, mock_load_workbook) -> None:
    """
    EN: Test reading classes from all sheets when wave_name is None.
    VI: Kiểm thử đọc lớp học từ tất cả các sheet khi wave_name là None.
    """
    mock_wb_instance = MagicMock()
    mock_wb_instance.sheetnames = ["Đợt 1", "Đợt 2"]
    mock_load_workbook.return_value = mock_wb_instance

    mock_load_excel.side_effect = [
        [{"Mã Lớp": "CLASS_A"}],
        [{"Mã Lớp": "CLASS_B"}]
    ]

    classes = ClassService.get_classes_from_excel("fake_path.xlsx", None)

    assert mock_load_workbook.called
    assert mock_load_excel.call_count == 2
    assert len(classes) == 2
    class_codes = [c.class_code for c in classes]
    assert "CLASS_A" in class_codes and "CLASS_B" in class_codes

@patch("apps.main_app.src.services.class_service.ClassService.save_wave_links")
@patch("os.path.exists")
@patch("openpyxl.Workbook")
def test_create_academic_year_file(mock_workbook, mock_exists, mock_save_links) -> None:
    """
    EN: Test creating a new academic year Excel file.
    VI: Kiểm thử tạo file Excel niên khóa mới.
    """
    mock_exists.return_value = False
    mock_wb_instance = MagicMock()
    mock_ws_instance = MagicMock()
    mock_workbook.return_value = mock_wb_instance
    mock_wb_instance.active = mock_ws_instance
    
    result = ClassService.create_academic_year_file("new_year.xlsx")
    
    assert result is True
    mock_ws_instance.append.assert_called_once()
    mock_wb_instance.save.assert_called_once_with("new_year.xlsx")
    mock_wb_instance.close.assert_called_once()
    mock_save_links.assert_called_once_with("new_year", "Đợt 1", "", "")
    
    # Test case: File already exists
    mock_exists.return_value = True
    result_exists = ClassService.create_academic_year_file("existing.xlsx")
    assert result_exists is False


@patch("apps.main_app.src.services.class_service.ClassService.update_class_in_wave_metadata")
@patch("apps.main_app.src.services.excel_service.ExcelService.save_row")
def test_save_class_to_excel(mock_save_row, mock_update_json) -> None:
    """
    EN: Test saving a planned ClassInfo object (10 characters) to Excel Sheet 1.
    VI: Kiểm thử lưu đối tượng Lớp dự kiến (Rổ - 10 ký tự) xuống Sheet 1 của Excel.
    """
    cls = ClassInfo(
        class_code="LNH0825NEA",
        year_code="2025-2026",
        class_name="Tiếng Anh Cấp Tốc Level 1",
        location="Cơ sở Q9",
        room="",
        session="Tối",
        schedule="3-5-7",
        time_slot="18:00 - 20:00",
        start_month_year="08/2025",
        end_date=date(2025, 12, 31),
        min_students=10,
        max_students=30,
        current_students=0,
        class_status="Dự kiến"
    )
    
    ClassService.save_class_to_excel("fake_path.xlsx", "Đợt 1", cls)
    
    mock_save_row.assert_called_once()
    mock_update_json.assert_called_once_with("2025-2026", "Đợt 1", "LNH0825NEA", "add")
    
    args, kwargs = mock_save_row.call_args
    
    assert kwargs["file_path"] == "fake_path.xlsx"
    assert "Mã Lớp" in kwargs["match_cols"]
    assert kwargs["match_value"] == "LNH0825NEA"
    assert kwargs["sheet_name"] == "Đợt 1"
    
    row_map = kwargs["row_data_map"]
    mapped_data = {aliases[0]: val for aliases, val in row_map}
    
    assert mapped_data["Mã Lớp"] == "LNH0825NEA"
    assert mapped_data["Tên Lớp"] == "Tiếng Anh Cấp Tốc Level 1"
    assert mapped_data["Trạng thái"] == "Dự kiến"
    assert mapped_data["SL Hiện tại"] == 0


@patch("apps.main_app.src.services.class_service.ClassService.update_class_in_wave_metadata")
@patch("apps.main_app.src.services.excel_service.ExcelService.delete_row")
def test_delete_class_from_excel(mock_delete_row, mock_update_json) -> None:
    """
    EN: Test deleting a class from Excel.
    VI: Kiểm thử xóa lớp học khỏi file Excel.
    """
    mock_delete_row.return_value = True
    
    result = ClassService.delete_class_from_excel("fake_path.xlsx", "2025-2026", "Đợt 1", "LNH0825NEA")
    
    assert result is True
    mock_update_json.assert_called_once_with("2025-2026", "Đợt 1", "LNH0825NEA", "remove")
    mock_delete_row.assert_called_once_with(
        file_path="fake_path.xlsx",
        match_cols=["Mã Lớp"],
        match_value="LNH0825NEA",
        sheet_name="Đợt 1"
    )


@patch("os.path.exists")
@patch("openpyxl.load_workbook")
def test_update_registration_counts(mock_load_workbook, mock_exists) -> None:
    mock_exists.return_value = True
    mock_wb = MagicMock()
    mock_load_workbook.return_value = mock_wb
    counts = {"LNH0825NEA": 5, "LNH0825NEB": 3}
    
    ClassService.update_registration_counts("fake.xlsx", "Đợt 1", counts)
    
    assert mock_load_workbook.called


@patch("os.makedirs")
@patch("os.path.exists")
@patch("os.listdir")
def test_get_academic_years(mock_listdir, mock_exists, mock_makedirs) -> None:
    """
    EN: Test scanning data directory for academic years.
    VI: Kiểm thử quét thư mục data để lấy danh sách niên khóa.
    """
    mock_exists.return_value = True
    mock_listdir.return_value = ["Quan Ly Lop Hoc 2025-2026.xlsx", "Danh Sach SV.xlsx", "Quan Ly Lop Hoc 2024-2025.xlsx"]
    
    years = ClassService.get_academic_years()
    
    assert len(years) == 2
    assert years[0] == "2025-2026"
    assert years[1] == "2024-2025"