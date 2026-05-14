import os
import json
import pytest
from unittest.mock import patch
from apps.main_app.src.services.class_wave_metadata_service import WaveMetadataService


def test_get_waves_for_year(tmp_path) -> None:
    """
    EN: Test parsing wave list from metadata JSON.
    VI: Kiểm thử lấy danh sách đợt từ file JSON cấu hình.
    """
    json_path = os.path.join(tmp_path, "form_links.json")
    data = {"2025-2026": {"Đợt 1": {}, "Đợt 2": {}}}
    with open(json_path, "w", encoding="utf-8") as f: json.dump(data, f)
    
    with patch("apps.main_app.src.services.class_wave_metadata_service.WaveMetadataService.get_form_links_file", return_value=json_path):
        waves = WaveMetadataService.get_waves_for_year("2025-2026")
        assert len(waves) == 2
        assert "Đợt 1" in waves
        assert "Đợt 2" in waves


def test_get_class_codes_for_wave(tmp_path) -> None:
    json_path = os.path.join(tmp_path, "form_links.json")
    data = {"2025-2026": {"Đợt 1": {"classes": ["LNH0825NEA", "LNH0825NEB"]}}}
    with open(json_path, "w", encoding="utf-8") as f: json.dump(data, f)
    
    with patch("apps.main_app.src.services.class_wave_metadata_service.WaveMetadataService.get_form_links_file", return_value=json_path):
        classes = WaveMetadataService.get_class_codes_for_wave("2025-2026", "Đợt 1")
        assert len(classes) == 2
        assert "LNH0825NEA" in classes


def test_get_wave_links(tmp_path) -> None:
    json_path = os.path.join(tmp_path, "form_links.json")
    data = {"2025-2026": {"Đợt 1": {"form_link": "link_f", "sheet_link": "link_s"}}}
    with open(json_path, "w", encoding="utf-8") as f: json.dump(data, f)
    
    with patch("apps.main_app.src.services.class_wave_metadata_service.WaveMetadataService.get_form_links_file", return_value=json_path):
        links = WaveMetadataService.get_wave_links("2025-2026", "Đợt 1")
        assert links["form_link"] == "link_f"
        assert links["sheet_link"] == "link_s"