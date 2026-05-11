import os
import openpyxl
from typing import List, Dict, Any


class ExcelService:
    """
    EN: Service to handle reading/writing Excel files.
    VI: Dịch vụ xử lý các thao tác đọc/ghi file Excel.
    """

    @staticmethod
    def load_excel_data(file_path: str, sheet_name: str | int = 0) -> List[Dict[str, Any]]:
        """
        EN: Load data from an Excel file into a list of dictionaries.
        VI: Đọc dữ liệu từ file Excel và chuyển thành danh sách dictionary.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File không tồn tại: {file_path}")

        try:
            # data_only=True giúp lấy giá trị tính toán cuối cùng thay vì công thức
            wb = openpyxl.load_workbook(file_path, data_only=True)
            
            if isinstance(sheet_name, int):
                ws = wb.worksheets[sheet_name]
            else:
                if sheet_name not in wb.sheetnames:
                    raise ValueError(f"Sheet '{sheet_name}' không tồn tại.")
                ws = wb[sheet_name]

            data = []
            headers = []
            empty_streak = 0
            
            for i, row in enumerate(ws.iter_rows(values_only=True)):
                if i == 0:
                    # Dòng đầu tiên là Header, ép về string
                    headers = [str(cell).strip() if cell is not None else f"Column_{j}" for j, cell in enumerate(row)]
                    print(f"📋 [DEBUG] Các cột Excel tìm thấy: {headers}")
                else:
                    # Bỏ qua các dòng trống hoàn toàn
                    if all(cell is None or str(cell).strip() == "" for cell in row):
                        empty_streak += 1
                        # Fail-safe chống treo máy: Dừng nếu gặp 50 dòng trống liên tiếp
                        if empty_streak > 50:
                            break
                        continue
                    
                    empty_streak = 0
                    # Map dữ liệu với Header, ép toàn bộ cell về string hoặc None
                    row_data = {
                        headers[j]: (str(cell).strip() if cell is not None and str(cell).strip() != "" else None)
                        for j, cell in enumerate(row) if j < len(headers)
                    }
                    data.append(row_data)
                    
            wb.close()
            return data
        except Exception as e:
            raise ValueError(f"Lỗi khi đọc file Excel {file_path}: {e}")

    @staticmethod
    def save_row(file_path: str, match_cols: List[str], match_value: str, row_data_map: List[tuple], sheet_name: str | int = 0) -> None:
        """
        EN: Update a row if match_value is found, else append a new row.
        VI: Cập nhật dòng nếu tìm thấy match_value, ngược lại thêm dòng mới.
        row_data_map: List of tuples (aliases_list, value)
        """
        if not os.path.exists(file_path):
            wb = openpyxl.Workbook()
            ws = wb.active
            if isinstance(sheet_name, str):
                ws.title = sheet_name
        else:
            # Lưu ý: Không dùng data_only=True để tránh mất công thức khi lưu
            wb = openpyxl.load_workbook(file_path)
            if isinstance(sheet_name, int):
                ws = wb.worksheets[sheet_name]
            else:
                if sheet_name not in wb.sheetnames:
                    ws = wb.create_sheet(sheet_name)
                ws = wb[sheet_name]

        # Đọc Header từ dòng 1
        headers = []
        for col_idx in range(1, ws.max_column + 1):
            cell_val = ws.cell(row=1, column=col_idx).value
            headers.append(str(cell_val).strip() if cell_val is not None else "")
            
        is_new_sheet = not any(headers)
        if is_new_sheet:
            for col_idx, (aliases, _) in enumerate(row_data_map, 1):
                ws.cell(row=1, column=col_idx, value=aliases[0])
                headers.append(aliases[0])

        # Tìm cột chứa ID để match (không phân biệt hoa thường)
        match_col_idx = -1
        match_cols_lower = [c.lower() for c in match_cols]
        for idx, header in enumerate(headers):
            if header.lower() in match_cols_lower:
                match_col_idx = idx
                break

        # Tìm dòng cuối cùng có dữ liệu thực sự (tránh lỗi max_row do format làm nhảy dòng)
        actual_max_row = 1
        for row_num in range(2, ws.max_row + 1):
            has_data = False
            for col_idx in range(1, len(headers) + 1):
                cell_val = ws.cell(row=row_num, column=col_idx).value
                if cell_val is not None and str(cell_val).strip() != "":
                    has_data = True
                    break
            if has_data:
                actual_max_row = row_num

        # Tìm xem dòng nào có ID khớp với match_value
        target_row_idx = -1
        if match_col_idx != -1:
            for row_num in range(2, actual_max_row + 1):
                cell_val = ws.cell(row=row_num, column=match_col_idx + 1).value
                if cell_val is not None and str(cell_val).strip().lower() == str(match_value).strip().lower():
                    target_row_idx = row_num
                    break

        # Nếu không tìm thấy, tạo dòng mới ở cuối
        if target_row_idx == -1:
            target_row_idx = actual_max_row + 1

        # Cập nhật dữ liệu vào các ô theo map
        headers_lower = [h.lower() for h in headers]
        
        for aliases, value in row_data_map:
            col_idx = -1
            aliases_lower = [a.lower() for a in aliases]
            for idx, h in enumerate(headers_lower):
                if h in aliases_lower:
                    col_idx = idx + 1
                    break
            
            if col_idx == -1:
                # Không tự động tạo cột mới nếu sheet đã có dữ liệu để tránh sinh rác
                if not is_new_sheet:
                    continue
                else:
                    col_idx = len(headers) + 1
                    ws.cell(row=1, column=col_idx, value=aliases[0])
                    headers.append(aliases[0])
                    headers_lower.append(aliases[0].lower())
                
            ws.cell(row=target_row_idx, column=col_idx, value=value)

        ExcelService._reindex_stt(ws)
        wb.save(file_path)
        wb.close()

    @staticmethod
    def delete_row(file_path: str, match_cols: List[str], match_value: str, sheet_name: str | int = 0) -> bool:
        """
        EN: Delete a row if match_value is found.
        VI: Xóa dòng nếu tìm thấy match_value.
        """
        if not os.path.exists(file_path):
            return False

        wb = openpyxl.load_workbook(file_path)
        if isinstance(sheet_name, int):
            ws = wb.worksheets[sheet_name]
        else:
            if sheet_name not in wb.sheetnames:
                return False
            ws = wb[sheet_name]

        headers = []
        for col_idx in range(1, ws.max_column + 1):
            cell_val = ws.cell(row=1, column=col_idx).value
            headers.append(str(cell_val).strip() if cell_val is not None else "")

        match_col_idx = -1
        match_cols_lower = [c.lower() for c in match_cols]
        for idx, header in enumerate(headers):
            if header.lower() in match_cols_lower:
                match_col_idx = idx
                break

        if match_col_idx != -1:
            for row_num in range(2, ws.max_row + 1):
                cell_val = ws.cell(row=row_num, column=match_col_idx + 1).value
                if cell_val is not None and str(cell_val).strip().lower() == str(match_value).strip().lower():
                    ws.delete_rows(row_num)
                    ExcelService._reindex_stt(ws)
                    wb.save(file_path)
                    wb.close()
                    return True
        wb.close()
        return False

    @staticmethod
    def _reindex_stt(ws) -> None:
        """
        EN: Re-calculate static STT (1, 2, 3...) for the sheet.
        VI: Đánh lại Số thứ tự tĩnh (1, 2, 3...) cho sheet.
        """
        header_row = 1
        headers = []
        for col_idx in range(1, ws.max_column + 1):
            cell_val = ws.cell(row=header_row, column=col_idx).value
            headers.append(str(cell_val).strip().lower() if cell_val is not None else "")
            
        stt_col_idx = -1
        for idx, h in enumerate(headers):
            if h in ["stt", "số tt", "số thứ tự"]:
                stt_col_idx = idx + 1
                break
                
        if stt_col_idx != -1:
            current_stt = 1
            for row_num in range(header_row + 1, ws.max_row + 1):
                has_data = False
                for col_idx in range(1, ws.max_column + 1):
                    if col_idx != stt_col_idx:
                        val = ws.cell(row=row_num, column=col_idx).value
                        if val is not None and str(val).strip() != "":
                            has_data = True
                            break
                if has_data:
                    ws.cell(row=row_num, column=stt_col_idx, value=current_stt)
                    current_stt += 1
                else:
                    ws.cell(row=row_num, column=stt_col_idx, value=None)