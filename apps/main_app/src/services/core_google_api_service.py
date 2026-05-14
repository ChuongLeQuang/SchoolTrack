import time
import logging
import re
import requests
from typing import Dict, List


class GoogleApiService:
    """
    EN: Service to handle communication with Google Apps Script and Google APIs.
    VI: Dịch vụ xử lý giao tiếp với Google Apps Script và các API của Google.
    """
    @staticmethod
    def auto_create_google_form(web_app_url: str, secret: str, template_id: str, wave_name: str, classes: List[str]) -> Dict[str, str]:
        start_time = time.time()
        logging.info(f"⏳ [TRAP-API] Bắt đầu gọi API tạo Form cho đợt: {wave_name}")
        payload = {"secret": secret, "wave_name": wave_name, "classes": classes, "template_id": template_id}
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.post(web_app_url, json=payload, timeout=60, allow_redirects=True)
                response.raise_for_status()
                try: 
                    res = response.json()
                    logging.info(f"✅ [TRAP-API] Hoàn tất gọi API tạo Form. Thời gian: {time.time() - start_time:.2f}s")
                    return res
                except Exception:
                    raw_text = response.text.strip()
                    if "<html" in raw_text.lower() or "<!doctype html>" in raw_text.lower():
                        return {
                            "status": "error", 
                            "message": "Google trả về trang Web (HTML) thay vì dữ liệu JSON.\n\nNguyên nhân thường gặp:\n1. Chưa chọn quyền truy cập là 'Bất kỳ ai' (Anyone) khi Deploy.\n2. URL Web App bị sai (phải kết thúc bằng /exec).\n3. Bạn copy nhầm Form ID hoặc thiếu quyền thao tác."
                        }
                    return {"status": "error", "message": f"Google phản hồi sai định dạng. Dữ liệu thô:\n{raw_text[:200]}"}
            except requests.exceptions.RequestException as e:
                logging.warning(f"Lỗi mạng khi gọi Google API. Thử lại {attempt + 1}/{retries}... Chi tiết: {e}")
                if attempt < retries - 1: time.sleep(2)
                else: return {"status": "error", "message": f"Mất kết nối máy chủ sau {retries} lần thử: {str(e)}"}
        return {"status": "error", "message": "Lỗi không xác định."}

    @staticmethod
    def download_google_sheet_as_excel(sheet_url: str, save_path: str) -> bool:
        start_time = time.time()
        logging.info(f"⏳ [TRAP-API] Bắt đầu tải file Google Sheet: {sheet_url}")
        if not sheet_url: return False
        id_match = re.search(r"spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
        if not id_match: return False
        sheet_id = id_match.group(1)
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
        resourcekey_match = re.search(r"resourcekey=([a-zA-Z0-9-_]+)", sheet_url)
        if resourcekey_match: export_url += f"&resourcekey={resourcekey_match.group(1)}"
        try:
            retries = 3
            for attempt in range(retries):
                try:
                    response = requests.get(export_url, stream=True, timeout=30)
                    response.raise_for_status()
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' in content_type:
                        logging.error(f"[LỖI TẢI FILE]: File Google Sheet bị khóa Private. Content-Type: {content_type}")
                        return False
                    with open(save_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192): f.write(chunk)
                    logging.info(f"✅ [TRAP-API] Hoàn tất tải file. Thời gian: {time.time() - start_time:.2f}s")
                    return True
                except requests.exceptions.RequestException as e:
                    logging.warning(f"Lỗi mạng tải file. Thử lại {attempt + 1}/{retries}... Chi tiết: {e}")
                    if attempt < retries - 1: time.sleep(2)
                    else:
                        logging.error(f"[LỖI TẢI FILE]: Request thất bại sau {retries} lần thử: {e}")
                        return False
            return False
        except Exception as e:
            logging.error(f"[LỖI KHÔNG XÁC ĐỊNH]: {e}")
            return False