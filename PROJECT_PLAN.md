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
  - **Mã Lớp**: Định dạng linh hoạt giữa Giai đoạn Dự kiến (9 ký tự) và Chính thức (11 ký tự) theo quy tắc:
    - **3 ký tự đầu**: Luôn luôn là `LNH`.
    - **2 ký tự kế tiếp**: Tháng khai giảng (VD: `08`).
    - **2 ký tự kế tiếp**: Năm khai giảng (2 số cuối, VD: `25` cho năm 2025).
    - **2 ký tự kế tiếp**: Cấp độ học (`NE` = Level 1, `ND` = Level 2, `NG` = Level 3, `NQ` = Level 4).
    => **Mã 9 ký tự** (VD: `LNH0825NE`): Là **Mã lớp dự kiến** (Rổ gom sinh viên).
    - **2 ký tự cuối cùng**: Từ `01` đến `20` (hoặc hơn). Phát sinh khi "Chốt lớp" phân bổ dựa trên số SV đăng ký.
    => **Mã 11 ký tự** (VD: `LNH0825NE01`): Là **Mã lớp vật lý chính thức**.
  - **Thông tin lớp**: Niên Khóa, Tên Lớp, Địa điểm, Ca học (Sáng/Chiều/Tối).
  - **Thời gian**: Khai giảng (tháng/năm), Ngày kết thúc dự kiến.
  - **Ràng buộc số lượng**: SL Min (để mở lớp), SL Max (giới hạn), SL Hiện tại.
  - **Trạng thái lớp**:  
    - `Đang mở` → đạt SL Min nhưng chưa đủ SL Max.
    - `Đã đủ` → đạt SL Max.
    - `Không mở` → không đạt SL Min sau hạn đăng ký.
    - `Đã đóng` → lớp đã kết thúc.

### 3. Đăng ký Lớp học (DangKySV)
- **Mục tiêu**: Quản lý việc sinh viên đăng ký lớp, phản ánh tiến trình theo từng thời điểm.
- **Cấu trúc & Trạng thái**:
  - Liên kết: **MSV** ↔ **Mã Lớp**.
  - **Trạng thái đăng ký**: 
    - `Đã đăng ký` → vừa đăng ký, chưa xác nhận.
    - `Hợp lệ` → thông tin hợp lệ, chờ thanh toán.
    - `Đã đóng học phí` → hoàn tất thanh toán.
    - `Đã phân bổ lớp` → đã được phân bổ vào lớp (khi lớp thực sự mở).

### 4. Quản lý Niên Khóa
- **Mục tiêu**: Gom lớp theo năm/kỳ học, lưu lịch sử và thống kê.
- **Thông tin**: Mã NK, Tên NK, Thời gian bắt đầu/kết thúc.
- **Thống kê**: Tổng lớp mở, Lớp giải tán, Tổng SV đăng ký, Tỉ lệ đạt yêu cầu.

---

## Phần II: Tiến Độ Triển Khai (Roadmap)

### Bước 1: Xử lý Dữ liệu (Tầng Model & Service)
- [x] Khởi tạo Data Model cốt lõi (`Student`, `ClassInfo`, `Registration`, `AcademicYear`)
- [x] Tích hợp engine đọc Excel an toàn (`openpyxl` & `ExcelService`)
- [x] Viết Unit Test & Service chuyển đổi dữ liệu Sinh viên (`StudentService`)
- [x] Viết Unit Test & Service chuyển đổi dữ liệu Lớp học (`ClassService`)
- [ ] Viết Unit Test & Service cho Đăng ký & Phân bổ lớp (`RegistrationService`)

### Bước 2: Thiết kế Giao Diện (Tầng UI/Views với PyQt6)
- [x] Thiết kế Layout tổng thể (Main Window) & Dashboard
- [ ] Thiết kế Menu điều hướng (Sidebar)
- [ ] Màn hình Quản lý Sinh viên (Hiển thị Data Table, Bộ lọc trạng thái)
- [ ] Màn hình Quản lý Lớp học (Quản lý SL Min/Max, Tiến độ ghi danh)
- [ ] Màn hình Đăng ký Lớp (Thêm SV vào lớp, Cập nhật trạng thái thanh toán)

### Bước 3: Mở rộng sau này
- [ ] Quản lý Giáo viên
- [ ] Quản lý Tài chính nâng cao
- [ ] Export Thống kê & Báo cáo
- [ ] Thông báo (Email/SMS)

---
*Ghi chú: Đánh dấu `[x]` vào các công việc đã hoàn thành để theo dõi tiến độ thực tế.*