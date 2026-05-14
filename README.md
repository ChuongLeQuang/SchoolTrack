# 🎓 SchoolTrack

**SchoolTrack** là giải pháp phần mềm Desktop toàn diện dành cho các trung tâm đào tạo. Hệ thống giúp số hóa vòng đời sinh viên, cung cấp công cụ trực quan để quản lý hồ sơ, lên kế hoạch mở lớp, tích hợp dữ liệu đăng ký từ Google Form và tự động hóa việc đối chiếu dữ liệu học phí với bộ phận Kế toán.

## ✨ Tính Năng Nổi Bật

- **🧑‍🎓 Quản lý Sinh viên**: Lưu trữ, tra cứu và cập nhật trạng thái học tập của sinh viên.
- **🏫 Kế hoạch Lớp học**: Tự động sinh mã lớp dự kiến (10 ký tự) dựa trên hệ thống cấu hình thông minh (Level, Ca học, Giờ học).
- **📝 Quản lý Niên khóa & Đợt**: Tổ chức dữ liệu theo từng "Đợt" (Sheet). Hệ thống chống trùng lặp tên đợt, tích hợp chế độ xem "Tất cả" an toàn. Hỗ trợ gắn link thủ công hoặc **tự động tạo Form/Sheet qua API 1-click**.
- **💰 Đối chiếu Kế toán**: Tự động đối chiếu file Excel của Kế toán với kết quả Form đăng ký. Bóc tách mã lớp/MSV bằng Regex thông minh, phân loại trạng thái (Hợp lệ, Lệch khớp, Chưa đóng tiền).
- **📊 Thống kê trực quan**: Bảng Dashboard (Sắp ra mắt), đếm số lượng đăng ký tự động và phân loại lớp (Mở/Hủy/Chờ).

## 🚀 Công Nghệ Sử Dụng

- **Ngôn ngữ**: Python 3.x
- **Giao diện (GUI)**: PyQt6
- **Xử lý Dữ liệu**: `openpyxl` (Đọc/Ghi Excel an toàn, không làm hỏng file gốc), `requests` (Tải file qua mạng).
- **Kiểm thử (Testing)**: `pytest` (với Mocking & Unit Tests bao phủ luồng nghiệp vụ).

<!-- ARCHITECTURE_START -->
## 🏗️ Cấu Trúc Dự Án (Kiến Trúc Phân Tầng)

Dự án được tổ chức theo mô hình **Monorepo** kết hợp kiến trúc phân tầng (Layered Architecture):

- `main.py`: Điểm neo khởi chạy ứng dụng (Entry Point) & hiển thị Splash Screen.
- `run_tests.py`: Kịch bản chạy toàn bộ Unit Tests tự động.
- `apps/main_app/src/`:
  - `models/`: Định nghĩa các cấu trúc dữ liệu cốt lõi (`Student`, `ClassInfo`, `AcademicYear`...).
  - `services/`: Xử lý nghiệp vụ logic (`StudentService`, `ClassService`, `RegistrationService`, `ExcelService`).
  - `views/`: Chứa các màn hình UI được thiết kế bằng PyQt6 (`MainWindow`, `StudentView`, `ClassView`).
  - `config/`: Chứa cấu hình JSON gốc (`class_templates.json`).
- `apps/main_app/data/`: Nơi lưu trữ an toàn các file CSDL Excel và Metadata hệ thống.
- `apps/main_app/tests/`: Tập hợp các bài kiểm thử tự động, ánh xạ 1:1 với cấu trúc của thư mục `src/`.
<!-- ARCHITECTURE_END -->

## ⚙️ Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Kích hoạt Môi trường ảo (.venv)
- **Windows**: `.\.venv\Scripts\activate`
- **Mac/Linux**: `source .venv/bin/activate`

### 2. Cài đặt thư viện (Chỉ làm lần đầu)
```bash
pip install -r requirements.txt
```

### 3. Khởi chạy Ứng dụng
```bash
python main.py
```

### 4. Khởi chạy Kiểm Thử (Unit Tests)
```bash
python run_tests.py
```

## 🔄 Đồng bộ Mã Nguồn (Dành cho Dev)
Sử dụng công cụ đã được viết sẵn để tự động Commit và Push code lên GitHub an toàn (hỗ trợ kiểm tra conflict, rebase tự động). Chỉ cần chạy lệnh:
```bash
.\sync.bat
```
