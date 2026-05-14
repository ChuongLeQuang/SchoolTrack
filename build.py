"""
EN: Build script to automate PyInstaller packaging.
VI: Kịch bản tự động hóa quá trình đóng gói ứng dụng bằng PyInstaller.
"""
import os
import sys
import subprocess
import platform
import shutil
from datetime import datetime

def get_next_version(file_path: str = "version.txt", bump_type: str = "current") -> str:
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f: current_version = f.read().strip()
    else: current_version = "1.0.0"
    if bump_type == "current": return current_version
    parts = current_version.split('.')
    if len(parts) >= 3:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        if bump_type == "major": return f"{major + 1}.0.0"
        elif bump_type == "minor": return f"{major}.{minor + 1}.0"
        else: return f"{major}.{minor}.{patch + 1}"
    return "1.0.1"

def create_version_file(version: str) -> str:
    parts = version.split('.')
    while len(parts) < 4: parts.append('0')
    vers_tuple = f"({parts[0]}, {parts[1]}, {parts[2]}, {parts[3]})"
    current_year = datetime.now().year

    content = f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(filevers={vers_tuple}, prodvers={vers_tuple}, mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[StringFileInfo([StringTable('040904B0', [
    StringStruct('CompanyName', 'Le Quang Chuong'),
    StringStruct('FileDescription', 'SchoolTrack Tool'),
    StringStruct('FileVersion', '{version}'),
    StringStruct('InternalName', 'SchoolTrack'),
    StringStruct('LegalCopyright', f'Copyright (c) {current_year} Le Quang Chuong'),
    StringStruct('OriginalFilename', 'SchoolTrack.exe'),
    StringStruct('ProductName', 'SchoolTrack'),
    StringStruct('ProductVersion', '{version}')])]), 
  VarFileInfo([VarStruct('Translation', [1033, 1200])])]
)"""
    file_path = "version_info.txt"
    with open(file_path, "w", encoding="utf-8") as f: f.write(content)
    return file_path

def ensure_init_files() -> None:
    for base_dir in ["src", "apps", "shared", "core"]:
        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                init_file = os.path.join(root, "__init__.py")
                if not os.path.exists(init_file):
                    with open(init_file, "w", encoding="utf-8") as f: pass

def build_app() -> None:
    if "--bump-only" in sys.argv:
        bump_type = "patch"
        if "--major" in sys.argv: bump_type = "major"
        elif "--minor" in sys.argv: bump_type = "minor"
        new_version = get_next_version(bump_type=bump_type)
        with open("version.txt", "w", encoding="utf-8") as f: f.write(new_version)
        print(f"✅ Đã cập nhật version.txt lên: {new_version}")
        sys.exit(0)

    print("🚀 Khởi động quá trình đóng gói ứng dụng...")
    try: import PyInstaller
    except ImportError:
        print("\n❌ Không tìm thấy thư viện 'pyinstaller'. Vui lòng chạy: pip install pyinstaller")
        sys.exit(1)
    
    for old_dir in ["build", "dist"]:
        if os.path.exists(old_dir): shutil.rmtree(old_dir, ignore_errors=True)

    ensure_init_files()
    bump_type = "current"
    if "--major" in sys.argv: bump_type = "major"
    elif "--minor" in sys.argv: bump_type = "minor"
    elif "--patch" in sys.argv: bump_type = "patch"

    new_version = get_next_version(bump_type=bump_type)
    print(f"📌 Phiên bản chuẩn bị build: {new_version}")

    app_name = "SchoolTrack"
    entry_point = "main.py"
    icon_path_ico = os.path.join("assets", "icon.ico")
    icon_path_png = os.path.join("assets", "icon.png")
    separator = os.pathsep
    
    pyinstaller_args = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed", f"--name={app_name}", "--paths=."]
    
    if not os.path.exists(icon_path_ico) and os.path.exists(icon_path_png) and platform.system() == "Windows":
        try:
            from PIL import Image
            img = Image.open(icon_path_png)
            img.save(icon_path_ico, format="ICO")
        except Exception: pass

    if os.path.exists(icon_path_ico): pyinstaller_args.append(f"--icon={icon_path_ico}")
    elif os.path.exists(icon_path_png) and platform.system() != "Windows": pyinstaller_args.append(f"--icon={icon_path_png}")
        
    if os.path.exists("assets"): pyinstaller_args.append(f"--add-data=assets{separator}assets")
    if os.path.exists(os.path.join("apps", "main_app", "src", "config")): pyinstaller_args.append(f"--add-data=apps/main_app/src/config{separator}config")
    if os.path.exists("templates"): pyinstaller_args.append(f"--add-data=templates{separator}templates")
    if os.path.exists("static"): pyinstaller_args.append(f"--add-data=static{separator}static")
    
    old_version = "1.0.0"
    if os.path.exists("version.txt"):
        with open("version.txt", "r", encoding="utf-8") as f: old_version = f.read().strip()
            
    with open("version.txt", "w", encoding="utf-8") as f: f.write(new_version)
    if os.path.exists("version.txt"): pyinstaller_args.append(f"--add-data=version.txt{separator}.")
    if os.path.exists("USER_GUIDE.md"): pyinstaller_args.append(f"--add-data=USER_GUIDE.md{separator}.")

    if platform.system() == "Windows":
        version_file = create_version_file(new_version)
        pyinstaller_args.append(f"--version-file={version_file}")
        
    pyinstaller_args.append(entry_point)
    
    try:
        subprocess.run(pyinstaller_args, check=True)
        print(f"\n✅ Đóng gói thành công '{app_name}'!")
        if platform.system() == "Windows" and os.path.exists("version_info.txt"): os.remove("version_info.txt")
        if os.path.exists(f"{app_name}.spec"): os.remove(f"{app_name}.spec")
        if os.path.exists("build"): shutil.rmtree("build")
    except subprocess.CalledProcessError as e:
        with open("version.txt", "w", encoding="utf-8") as f: f.write(old_version)
        print(f"\n❌ Có lỗi xảy ra: {e}")
        sys.exit(1)
    except FileNotFoundError:
        with open("version.txt", "w", encoding="utf-8") as f: f.write(old_version)
        print("\n❌ Lỗi hệ thống!")
        sys.exit(1)

if __name__ == "__main__":
    build_app()
