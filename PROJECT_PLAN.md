# 📌 Kế Hoạch & Đặc Tả Dự Án: SchoolTrack

Tài liệu này định nghĩa chi tiết về cấu trúc dữ liệu, luồng nghiệp vụ cốt lõi và tiến độ triển khai của hệ thống quản lý SchoolTrack.

---

## Phần I: Đặc Tả Nghiệp Vụ & Dữ Liệu

### 1. Quản lý Sinh viên (SV)
- **Mục tiêu**: Lưu trữ và quản lý thông tin cá nhân, theo dõi tình trạng học tập tổng thể của sinh viên.  
- **Cấu trúc & Trạng thái**:
  - **Mã Sinh viên (MSV)**: khóa chính, duy nhất.
  - **Thông tin cơ bản**: Họ tên, Ngày sinh, Email, Số điện thoại.
  - **Trạng thái học tập**: 
    - `Đang học` → đang theo học.
    - `Tạm nghỉ` → xin nghỉ tạm thời.
    - `Nghỉ học` → bỏ học, không tiếp tục.
    - `Tốt nghiệp` → đã hoàn thành chương trình.
    - `Khác` → trường hợp đặc biệt (chuyển trường, thôi học…).  
- **Liên kết**: MSV ↔ Đăng ký lớp học (DangKySV).

### 2. Quản lý Lớp học (QLLH)
- **Mục tiêu**: Quản lý chi tiết từng lớp học trong một niên khóa.
- **Cấu trúc & Trạng thái**:
  - **Mã Lớp**: Định dạng linh hoạt cho Lớp dự kiến (10 ký tự) và Lớp chính thức theo quy tắc:
    - **3 ký tự đầu**: Luôn luôn là `LNH`.
    - **2 ký tự kế tiếp**: Tháng khai giảng (VD: `08`).
    - **2 ký tự kế tiếp**: Năm khai giảng (2 số cuối, VD: `25` cho năm 2025).
    - **2 ký tự kế tiếp**: Cấp độ học (`NE` = Level 1, `ND` = Level 2, `NG` = Level 3, `NQ` = Level 4).
    - **1 ký tự phân biệt rổ**: `A`, `B`, `C`... (VD: `LNH0825NEA` - 10 ký tự) - Là **Mã lớp dự kiến** (Rổ gom đăng ký).
    - **Hậu tố lớp chính thức**: Phát sinh khi "Chốt lớp" phân bổ (có thể thêm số thứ tự `01`, `02` thành 12 ký tự hoặc giữ nguyên 10 ký tự tùy quy mô).
  - **Thông tin lớp**: Niên Khóa, Tên Lớp, Địa điểm, Ca học (Sáng/Chiều/Tối).
  - **Thời gian**: Khai giảng (tháng/năm), Ngày kết thúc dự kiến.
  - **Ràng buộc số lượng**: SL Min (để mở lớp), SL Max (giới hạn), SL Hiện tại.
  - **Trạng thái lớp**:  
    - `Đang mở` → đạt SL Min nhưng chưa đủ SL Max.
    - `Đã đủ` → đạt SL Max.
    - `Không mở` → không đạt SL Min sau hạn đăng ký.
    - `Đã đóng` → lớp đã kết thúc.

### 3. Đăng ký Lớp học (DangKySV)
- **Mục tiêu**: Thu thập nguyện vọng từ Google Form, đối chiếu đóng tiền với file Kế toán.
- **Cấu trúc & Trạng thái**:
  - Liên kết: **MSV** ↔ **Mã Lớp**.
  - **Trạng thái đăng ký**: 
    - `Nguyện vọng` → mới nộp form, chưa đóng tiền.
    - `Lệch khớp` → đóng tiền nhưng sai MSV/Mã lớp.
    - `Hợp lệ` → khớp MSV, Mã lớp và đã đóng học phí.
    - `Đã phân bổ lớp` → đã được phân bổ vào lớp (khi lớp thực sự mở).

### 4. Quản lý Niên Khóa & Đợt (Wave)
- **Mục tiêu**: Tổ chức dữ liệu lớp học theo cấp bậc `Niên khóa` > `Đợt khai giảng` (Sheet trong Excel).
- **Thông tin**: Niên khóa (VD: 2025-2026), Đợt (VD: Đợt 1, Đợt 2). Mỗi Đợt đi kèm 1 cấu hình Link Google Form & Sheet riêng.
- **Thống kê**: Tổng lớp mở, Lớp giải tán, Tổng SV đăng ký, Tỉ lệ đạt yêu cầu.

---

## Phần II: Tiến Độ Triển Khai (Roadmap)

### Bước 1: Xử lý Dữ liệu (Tầng Model & Service)
- [x] Khởi tạo Data Model cốt lõi (`Student`, `ClassInfo`, `Registration`, `AcademicYear`)
- [x] Tích hợp engine đọc Excel an toàn (`openpyxl` & `ExcelService`)
- [x] Viết Unit Test & Service chuyển đổi dữ liệu Sinh viên (`StudentService`)
- [x] Viết Unit Test & Service chuyển đổi dữ liệu Lớp học (`ClassService`)
- [x] Viết Unit Test & Service cho Đăng ký & Phân bổ lớp (`RegistrationService`)

### Bước 2: Thiết kế Giao Diện (Tầng UI/Views với PyQt6)
- [x] Thiết kế Layout tổng thể (Main Window) & Dashboard
- [x] Thiết kế Menu điều hướng (Sidebar)
- [x] Màn hình Quản lý Sinh viên (Hiển thị Data Table, Bộ lọc trạng thái, CRUD)
- [x] Màn hình Quản lý Lớp học: Tab 1 - Kế hoạch Dự kiến (Tự sinh mã lớp, Nhúng Excel Google Form)
- [ ] Màn hình Quản lý Lớp học: Tab 2 - Đối chiếu Kế toán (Gộp danh sách đóng tiền)
- [ ] Màn hình Quản lý Lớp học: Tab 3 - Chốt Lớp & Phân bổ (Mở/Hủy lớp)

### Bước 3: Mở rộng sau này
- [ ] Quản lý Giáo viên
- [ ] Quản lý Tài chính nâng cao
- [ ] Export Thống kê & Báo cáo
- [ ] Thông báo (Email/SMS)

---
*Ghi chú: Đánh dấu `[x]` vào các công việc đã hoàn thành để theo dõi tiến độ thực tế.*