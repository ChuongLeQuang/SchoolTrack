import json
import os
import sys
from typing import Dict, Any


class ConfigService:
    """
    EN: Service to handle application configurations.
    VI: Dịch vụ xử lý các cấu hình của ứng dụng.
    """
    
    @staticmethod
    def _get_config_path() -> str:
        if getattr(sys, 'frozen', False):
            project_root = os.path.dirname(sys.executable)
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        return os.path.join(project_root, "apps", "main_app", "src", "config", "class_templates.json")

    @staticmethod
    def get_config_data(file_path: str = None) -> Dict[str, Any]:
        if file_path is None:
            file_path = ConfigService._get_config_path()
            
        if not os.path.exists(file_path):
            return {}
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @staticmethod
    def save_config_data(data: Dict[str, Any], file_path: str = None) -> bool:
        if file_path is None:
            file_path = ConfigService._get_config_path()
            
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception:
            return False

    @staticmethod
    def add_new_location(location: str, file_path: str = None) -> None:
        location = location.strip()
        if not location:
            return
        data = ConfigService.get_config_data(file_path)
        locations = data.get("locations", [])
        if location not in locations:
            locations.append(location)
            data["locations"] = locations
            ConfigService.save_config_data(data, file_path)

    @staticmethod
    def add_new_schedule(schedule: str, file_path: str = None) -> None:
        schedule = schedule.strip()
        if not schedule:
            return
        data = ConfigService.get_config_data(file_path)
        schedules = data.get("schedules", [])
        if schedule not in schedules:
            schedules.append(schedule)
            data["schedules"] = schedules
            ConfigService.save_config_data(data, file_path)

    @staticmethod
    def add_new_time_slot(time_slot: str, file_path: str = None) -> None:
        time_slot = time_slot.strip()
        if not time_slot:
            return
        data = ConfigService.get_config_data(file_path)
        time_slots = data.get("time_slots", [])
        if time_slot not in time_slots:
            time_slots.append(time_slot)
            data["time_slots"] = time_slots
            ConfigService.save_config_data(data, file_path)

    @staticmethod
    def get_class_templates(file_path: str = None) -> Dict[str, Any]:
        data = ConfigService.get_config_data(file_path)
        return data.get("class_templates", {})

    @staticmethod
    def get_locations(file_path: str = None) -> list:
        data = ConfigService.get_config_data(file_path)
        return data.get("locations", ["Cơ sở Q9", "Cơ sở Q1"])

    @staticmethod
    def get_sessions(file_path: str = None) -> list:
        data = ConfigService.get_config_data(file_path)
        return data.get("sessions", ["Sáng", "Chiều", "Tối"])

    @staticmethod
    def get_schedules(file_path: str = None) -> list:
        data = ConfigService.get_config_data(file_path)
        return data.get("schedules", ["2-4-6", "3-5-7", "T7-CN"])

    @staticmethod
    def get_time_slots(file_path: str = None) -> list:
        data = ConfigService.get_config_data(file_path)
        return data.get("time_slots", ["08:00 - 10:00", "14:00 - 16:00", "18:00 - 20:00"])