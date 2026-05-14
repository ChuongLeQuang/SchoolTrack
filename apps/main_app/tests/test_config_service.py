import pytest
import json
import os
from apps.main_app.src.services.core_config_service import ConfigService


def test_get_class_templates(tmp_path) -> None:
    """
    EN: Test loading class templates from a JSON file.
    VI: Kiểm thử việc đọc danh sách mẫu lớp học từ file JSON.
    """
    mock_file = os.path.join(tmp_path, "class_templates.json")
    data = {
        "class_templates": {
            "TEST": {"name": "Test Class", "min": 15, "max": 30, "session": "Sáng", "schedule": "2-4-6", "time_slot": "08:00 - 10:00", "location": "Cơ sở Q9"}
        }
    }
    with open(mock_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    templates = ConfigService.get_class_templates(mock_file)
    assert "TEST" in templates
    assert templates["TEST"]["name"] == "Test Class"
    

def test_get_class_templates_not_found() -> None:
    templates = ConfigService.get_class_templates("non_existent.json")
    assert templates == {}


def test_get_locations_and_time_options(tmp_path) -> None:
    mock_file = os.path.join(tmp_path, "class_templates.json")
    data = {
        "locations": ["L1", "L2"],
        "sessions": ["Ses1"],
        "schedules": ["Sch1"],
        "time_slots": ["TS1"]
    }
    with open(mock_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    locations = ConfigService.get_locations(mock_file)
    sessions = ConfigService.get_sessions(mock_file)
    schedules = ConfigService.get_schedules(mock_file)
    
    assert len(locations) == 2
    assert locations[0] == "L1"
    assert len(sessions) == 1
    assert sessions[0] == "Ses1"
    assert len(schedules) == 1
    assert schedules[0] == "Sch1"


def test_save_and_add_new_options(tmp_path) -> None:
    """
    EN: Test saving new locations, schedules and time slots to config.
    VI: Kiểm thử việc lưu địa điểm và thời gian mới vào cấu hình.
    """
    mock_file = os.path.join(tmp_path, "class_templates.json")
    data = {"locations": ["OldLoc"], "schedules": ["OldSch"], "time_slots": ["OldTS"]}
    with open(mock_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
        
    # Thêm địa điểm mới
    ConfigService.add_new_location("NewLoc", mock_file)
    locations = ConfigService.get_locations(mock_file)
    assert "NewLoc" in locations
    assert len(locations) == 2
    
    # Thêm lịch học mới
    ConfigService.add_new_schedule("NewSch", mock_file)
    schedules = ConfigService.get_schedules(mock_file)
    assert "NewSch" in schedules
    assert len(schedules) == 2
    
    # Thêm giờ học mới
    ConfigService.add_new_time_slot("NewTS", mock_file)
    time_slots = ConfigService.get_time_slots(mock_file)
    assert "NewTS" in time_slots
    assert len(time_slots) == 2