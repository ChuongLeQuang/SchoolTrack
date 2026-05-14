import os
import sys
import json
from typing import List


class WaveMetadataService:
    """
    EN: Service to handle metadata of waves (links and associated classes) stored in JSON.
    VI: Dịch vụ xử lý siêu dữ liệu của các đợt (link và lớp liên kết) lưu trong file JSON.
    """
    @staticmethod
    def get_data_dir() -> str:
        if getattr(sys, 'frozen', False):
            project_root = os.path.dirname(sys.executable)
            data_dir = os.path.join(project_root, "data")
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            data_dir = os.path.join(project_root, "apps", "main_app", "data")
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        return data_dir

    @staticmethod
    def get_form_links_file() -> str:
        return os.path.join(WaveMetadataService.get_data_dir(), "form_links.json")

    @staticmethod
    def get_waves_for_year(year: str) -> List[str]:
        file_path = WaveMetadataService.get_form_links_file()
        if not os.path.exists(file_path): return []
        try:
            with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
            year_data = data.get(year, {})
            if isinstance(year_data, dict): return list(year_data.keys())
        except (FileNotFoundError, json.JSONDecodeError): return []
        return []

    @staticmethod
    def get_class_codes_for_wave(year: str, wave: str) -> List[str]:
        file_path = WaveMetadataService.get_form_links_file()
        if not os.path.exists(file_path): return []
        try:
            with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
            year_data = data.get(year, {})
            wave_data = year_data.get(wave, {})
            if isinstance(wave_data, dict): return wave_data.get("classes", [])
        except (FileNotFoundError, json.JSONDecodeError): return []
        return []

    @staticmethod
    def get_wave_links(year: str, wave: str) -> dict:
        file_path = WaveMetadataService.get_form_links_file()
        default_links = {"form_link": "", "sheet_link": ""}
        if not os.path.exists(file_path): return default_links
        try:
            with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
            year_data = data.get(year, {})
            wave_data = year_data.get(wave, {})
            old_key = f"{year}_{wave}"
            if old_key in data: wave_data = data[old_key]
            if isinstance(wave_data, str): return {"form_link": wave_data, "sheet_link": ""}
            elif isinstance(wave_data, dict): return {"form_link": wave_data.get("form_link", ""), "sheet_link": wave_data.get("sheet_link", "")}
            return default_links
        except (FileNotFoundError, json.JSONDecodeError): return default_links

    @staticmethod
    def save_wave_links(year: str, wave: str, form_link: str, sheet_link: str) -> None:
        file_path = WaveMetadataService.get_form_links_file()
        data = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError): pass
        if year not in data or not isinstance(data[year], dict): data[year] = {}
        if wave not in data[year]: data[year][wave] = {"form_link": "", "sheet_link": "", "classes": []}
        data[year][wave]["form_link"] = form_link
        data[year][wave]["sheet_link"] = sheet_link
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def update_class_in_wave_metadata(year: str, wave: str, class_code: str, action: str) -> None:
        file_path = WaveMetadataService.get_form_links_file()
        data = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError): pass
        if year not in data or not isinstance(data[year], dict): data[year] = {}
        if wave not in data[year]: data[year][wave] = {"form_link": "", "sheet_link": "", "classes": []}
        if "classes" not in data[year][wave]: data[year][wave]["classes"] = []
        classes = data[year][wave]["classes"]
        if action == "add" and class_code not in classes: classes.append(class_code)
        elif action == "remove" and class_code in classes: classes.remove(class_code)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def rename_wave_metadata(year: str, old_wave_name: str, new_wave_name: str) -> None:
        links_file = WaveMetadataService.get_form_links_file()
        if os.path.exists(links_file):
            try:
                with open(links_file, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    changed = False
                    old_flat_key = f"{year}_{old_wave_name}"
                    if old_flat_key in data:
                        if year not in data or not isinstance(data[year], dict): data[year] = {}
                        data[year][new_wave_name] = data.pop(old_flat_key)
                        changed = True
                    if year in data and isinstance(data[year], dict) and old_wave_name in data[year]:
                        data[year][new_wave_name] = data[year].pop(old_wave_name)
                        changed = True
                    if changed:
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4, ensure_ascii=False)
            except (OSError, PermissionError):
                # EN: Catch file manipulation errors when renaming wave.
                # VI: Bắt lỗi thao tác file khi đổi tên đợt.
                pass

    @staticmethod
    def delete_wave_metadata(year: str, wave_name: str) -> None:
        links_file = WaveMetadataService.get_form_links_file()
        if os.path.exists(links_file):
            try:
                with open(links_file, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    changed = False
                    old_flat_key = f"{year}_{wave_name}"
                    if old_flat_key in data:
                        data.pop(old_flat_key)
                        changed = True
                    if year in data and isinstance(data[year], dict) and wave_name in data[year]:
                        data[year].pop(wave_name)
                        if not data[year]: data.pop(year)
                        changed = True
                    if changed:
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4, ensure_ascii=False)
            except (OSError, PermissionError):
                # EN: Catch file manipulation errors when deleting wave.
                # VI: Bắt lỗi thao tác file khi xóa đợt.
                pass