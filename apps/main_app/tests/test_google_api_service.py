import pytest
from unittest.mock import patch, MagicMock
from apps.main_app.src.services.core_google_api_service import GoogleApiService


@patch("requests.post", autospec=True)
def test_auto_create_google_form_success(mock_post) -> None:
    """
    EN: Test successful Google Form creation API call.
    VI: Kiểm thử gọi API tạo Form thành công trả về JSON.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "success", "form_url": "http://form.com", "sheet_url": "http://sheet.com"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = GoogleApiService.auto_create_google_form("url", "secret", "tpl_id", "Đợt 1", ["Class A"])
    
    assert result["status"] == "success"
    assert result["form_url"] == "http://form.com"
    assert result["sheet_url"] == "http://sheet.com"


@patch("requests.post", autospec=True)
def test_auto_create_google_form_html_error(mock_post) -> None:
    """
    EN: Test API fallback when Google returns HTML instead of JSON.
    VI: Kiểm thử bắt lỗi khi Google trả về HTML thay vì JSON (Lỗi quyền truy cập).
    """
    mock_response = MagicMock()
    mock_response.json.side_effect = Exception("Not JSON")
    mock_response.text = "<!DOCTYPE html><html>Bạn cần đăng nhập</html>"
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = GoogleApiService.auto_create_google_form("url", "secret", "tpl", "wave", ["c1"])
    assert result["status"] == "error"
    assert "Google trả về trang Web (HTML)" in result["message"]