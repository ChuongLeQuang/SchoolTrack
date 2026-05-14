# 📌 Kế Hoạch & Đặc Tả Dự Án: SchoolTrack

Tài liệu này định nghĩa chi tiết về cấu trúc dữ liệu, luồng nghiệp vụ cốt lõi và tiến độ triển khai của hệ thống quản lý SchoolTrack.

---

## Phần I: Đặc Tả Nghiệp Vụ & Dữ Liệu

### 1. Quản lý Sinh viên (SV)
- **Mục tiêu**: Lưu trữ và quản lý thông tin cá nhân, theo dõi tình trạng học tập tổng thể của sinh viên.  
- **Cấu trúc & Trạng thái**:
  - **Mã Sinh viên (MSV)**: khóa chính, duy nhất.
  - **Thông tin cơ bản**: Họ tên, Ngày sinh, Email, Số điện thoại.
  - **Số dư học phí**: Theo dõi công nợ của sinh viên.
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
    - **Mã lớp chính thức (11 ký tự)**: Phát sinh khi "Chốt lớp". Lấy 9 ký tự đầu của Mã lớp dự kiến và thêm số thứ tự (VD: `01`, `02`). Ví dụ: `LNH0825NEA` sẽ trở thành `LNH0825NE01`.
  - **Thông tin lớp**: Niên Khóa, Tên Lớp, Địa điểm, Ca học (Sáng/Chiều/Tối).
  - **Thời gian**: Khai giảng (tháng/năm), Ngày kết thúc dự kiến.
  - **Ràng buộc số lượng**: SL Min (để mở lớp), SL Max (giới hạn), SL Hiện tại.
  - **Trạng thái lớp**:
    - `Dự kiến`: Lớp đang trong giai đoạn lên kế hoạch, gom đăng ký.
    - `Chính thức`: Lớp đã được chốt mở (sẽ được triển khai ở Tab 3).
    - `Đã hủy`: Lớp không đủ SL Min và bị hủy (sẽ được triển khai ở Tab 3).
    - `Kết thúc`: Lớp đã hoàn thành chương trình học.

### 3. Đăng ký Lớp học (DangKySV)
- **Mục tiêu**: Thu thập nguyện vọng từ Google Form, đối chiếu đóng tiền với file Kế toán.
- **Cấu trúc & Trạng thái**:
  - Liên kết: **MSV** ↔ **Mã Lớp**.
  - **Trạng thái đăng ký**: 
    - `Nguyện vọng` → mới nộp form, chưa đóng tiền.
    - `Lệch khớp` → đóng tiền nhưng sai MSV/Mã lớp, hoặc có nộp form nhưng không thấy chuyển khoản.
    - `Hợp lệ` → khớp MSV, Mã lớp và đã đóng học phí.
    - `Đã phân bổ lớp` → đã được phân bổ vào lớp (khi lớp thực sự mở).

### 4. Quản lý Niên Khóa & Đợt (Wave)
- **Mục tiêu**: Tổ chức dữ liệu lớp học theo cấp bậc `Niên khóa` > `Đợt khai giảng` (Sheet trong Excel).
- **Thông tin**: Niên khóa (VD: 2025-2026), Đợt (VD: Đợt 1, Đợt 2). Mỗi Đợt đi kèm 1 cấu hình Link Google Form & Sheet riêng.
- **Thống kê**: Tổng lớp mở, Lớp giải tán, Tổng SV đăng ký, Tỉ lệ đạt yêu cầu.
- **Quy tắc nghiệp vụ**:
  - **Chuẩn hóa Tên Đợt**: Tên Đợt được tự động chuẩn hóa (loại bỏ khoảng trắng thừa, kiểm tra trùng lặp không phân biệt hoa/thường) để đảm bảo tính toàn vẹn dữ liệu trên Excel.
  - **Chế độ "Tất cả"**: Chế độ xem tổng hợp toàn bộ các lớp của một niên khóa. Khi kích hoạt, toàn bộ chức năng thao tác dữ liệu (Thêm, Sửa, Xóa, Cập nhật...) bị khóa tạm thời để bảo vệ an toàn cho file gốc.
  - **Tự động hóa Google Form**: Tích hợp API qua Google Apps Script (GAS). Cho phép 1-click tự động nhân bản Form mẫu, chèn danh sách lớp, tạo Sheet liên kết và cấp quyền truy cập (Áp dụng linh hoạt cho cả tài khoản Google Cá nhân & Doanh nghiệp).

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
- [x] Tích hợp Splash Screen khi khởi động ứng dụng.
- [x] Thiết kế Menu điều hướng (Sidebar)
- [x] Tích hợp Cửa sổ Hướng dẫn sử dụng (truy cập từ Sidebar).
- [x] Màn hình Quản lý Sinh viên (Hiển thị Data Table, Bộ lọc trạng thái, CRUD)
- [x] Màn hình Quản lý Lớp học: Tab 1 - Kế hoạch Dự kiến (Tự sinh mã lớp, API tạo Form tự động, Cập nhật SL thông minh chống nhiễu & Reset rổ)
- [x] Màn hình Quản lý Lớp học: Tab 2 - Đối chiếu Kế toán (Quét Regex lấy MSV/Mã lớp từ lịch sử giao dịch, đối chiếu Hợp lệ/Lệch khớp/Chưa đóng tiền)
- [ ] Màn hình Quản lý Lớp học: Tab 3 - Chốt Lớp & Phân bổ (Mở/Hủy lớp)

### Bước 3: Mở rộng sau này
- [ ] **Data Enrichment (Tự động làm giàu hồ sơ Sinh viên từ Form)**:
  - **Mục tiêu**: Lợi dụng quá trình sinh viên điền Google Form để thu thập thêm Số điện thoại, Email mới và làm sạch dữ liệu Họ Tên (hỗ trợ chuyển từ không dấu thành có dấu chuẩn chỉnh).
  - **Thay đổi Cấu trúc (Data Model)**:
    - Cập nhật entity `Student`: Các trường `phone_number` và `email` chuyển từ chuỗi (`str`) sang mảng (`List[str]`).
    - Cập nhật `ExcelService`: Hỗ trợ đọc/ghi danh sách phân cách bằng dấu phẩy (VD: `090123, 090456`).
    - Cập nhật bộ lọc Thông minh (Tab 1, Tab 2): Chuyển logic từ so sánh chuỗi bằng (==) sang kiểm tra tồn tại trong mảng (in).
  - **Luồng xử lý (Thuật toán "Bộ lọc Kép")**:
    - **Vòng 1 (Xác thực ưu tiên - Giữ dấu)**: Chuyển tên Form và tên DB về chữ thường, chuẩn hóa bảng mã Unicode (NFC), *giữ nguyên dấu* (Dùng module mới `name_matcher.py`). Dùng `difflib` chấm điểm. Khớp >= 95% -> Chấp nhận đăng ký (vượt qua vòng xác thực).
    - **Vòng 2 (Vớt vát - Gọt dấu & Đề xuất sửa tên)**: Nếu Vòng 1 < 95%, đưa cả 2 tên qua "Máy mài" để *gọt sạch dấu* và so sánh lại.
      - Khớp >= 95% (sau khi gọt dấu): Vẫn chấp nhận đăng ký. ĐỒNG THỜI, đưa vào hàng đợi `[Đề xuất Sửa Tên]` để Admin quyết định có lấy tên có dấu trên Form đè lên tên không dấu trong DB hay không.
      - Khớp < 95% (kể cả sau khi gọt dấu): Khóa, từ chối bản đăng ký vì nghi ngờ sai người/mượn MSV.
    - Quét SĐT/Email (Làm giàu): Dùng Regex kiểm tra SĐT/Email. Nếu là thông tin MỚI chưa có trong hệ thống -> Đưa vào hàng đợi đề xuất Thêm vào (Append).
  - **UX/UI (Trạm Kiểm Duyệt)**:
    - Lưu trữ trung gian: Kết quả quét được lưu ngầm vào `data/pending_updates.json` để Admin có thể dừng duyệt bất cứ lúc nào và tiếp tục vào ngày hôm sau.
    - Giao diện: Tạo một Dialog hiển thị danh sách dạng bảng: `[MSV] | [Loại thay đổi] | [Thông tin Cũ] ➡️ [Thông tin Mới] | [Nút Duyệt] [Nút Bỏ Qua]`.
    - Hành động: Khi nhấn "Duyệt", hệ thống cập nhật thẳng vào file `Danh Sach SV.xlsx` và xóa dòng đó khỏi file JSON. Nếu chọn "Bỏ qua", chỉ xóa khỏi JSON, tuyệt đối không ảnh hưởng đến lượt đăng ký lớp hợp lệ của sinh viên.
  - **WBS (Work Breakdown Structure) Chi Tiết**:
    - **Task 1: Tạo Lõi so sánh tên (Utils)**
      - Tạo file mới `src/utils/name_matcher.py` để xử lý so sánh tên (Không sửa `text_utils.py` để tránh break code cũ).
      - Viết hàm `normalize_for_strict_match` (Vòng 1: NFC, chữ thường).
      - Viết hàm `compare_names_hybrid` xử lý luồng Vòng 1 & Vòng 2.
    - **Task 2: Cấu trúc hóa SĐT/Email & Lõi Quét Làm Giàu (Service)**
      - Cập nhật `student_service.py` (`get_students_from_excel`) để đọc và gom SĐT/Email thành danh sách phân cách dấu phẩy.
      - Thêm hàm `scan_form_for_enrichment` độc lập trong `StudentService` để quy hoạch đúng miền nghiệp vụ Sinh viên.
    - **Task 3: Trả lại sự trong sạch cho Registration Service (Refactor)**
      - Bóc tách toàn bộ mã quét SĐT/Email/Tên ra khỏi `registration_service.py`. Service này chỉ tập trung vào việc đếm số lượng đăng ký lớp học (áp dụng `name_matcher.py` để xác thực), không can thiệp sửa đổi hồ sơ sinh viên.
    - **Task 4: Xây dựng Sub-menu & Trạm Kiểm Duyệt (UI)**
      - Tạo file mới `data_enrichment_view.py` chứa giao diện quét và duyệt.
      - Thêm Sub-menu "2. Làm giàu Dữ liệu" vào mục "Quản lý Sinh viên" trong Sidebar của `main_window.py`.
  - **Báo cáo Đối chiếu chéo (Cross-Audit)**:
    | Yêu cầu Thiết kế | Task WBS tương ứng | Trạng thái |
    | --- | --- | --- |
    | Tách biệt code, không ảnh hưởng logic cũ | Task 1 (`name_matcher.py`) | ✅ Pass |
    | Bộ lọc Kép (Giữ dấu -> Gọt dấu) | Task 1 + Task 3 | ✅ Pass |
    | Làm giàu SĐT/Email an toàn | Task 2 + Task 3 | ✅ Pass |
    | Giao diện duyệt có khả năng lưu dở dang | Task 3 (Ghi JSON) + Task 4 (Đọc JSON/UI) | ✅ Pass |
- [ ] Quản lý Giáo viên
- [ ] Quản lý Tài chính nâng cao
- [ ] Export Thống kê & Báo cáo
- [ ] Thông báo (Email/SMS)

---

## Phần III: Cấu Trúc Thư Mục Dự Án

Dự án được tổ chức theo mô hình Monorepo với cấu trúc phân tầng rõ ràng, tuân thủ các quy tắc đã định nghĩa trong `AI_RULES.md`.

```
SchoolTrack/
├── .venv/                          # Môi trường ảo của Python
├── apps/                           # Chứa các ứng dụng con (main_app là ứng dụng Desktop chính)
│   └── main_app/                   # Ứng dụng Desktop chính
│       ├── data/                   # Nơi lưu trữ các file dữ liệu Excel của người dùng (Danh Sach SV.xlsx, Quan Ly Lop Hoc.xlsx)
│       ├── src/                    # Mã nguồn chính của ứng dụng
│       │   ├── config/             # Chứa các file cấu hình tĩnh (class_templates.json)
│       │   ├── models/             # Định nghĩa các đối tượng dữ liệu (entities)
│       │   ├── services/           # Xử lý logic nghiệp vụ, tương tác với dữ liệu
│       │   ├── utils/              # Chứa các hàm tiện ích dùng chung (VD: text_utils.py xử lý tiếng Việt)
│       │   └── views/              # Chứa các file giao diện người dùng (PyQt6 UI)
│       └── tests/                  # Các bài kiểm thử đơn vị (Unit Tests)
│           ├── services/           # Unit Tests cho các Service
│           └── views/              # Unit Tests cho các View/Dialog
├── assets/                         # Chứa các tài nguyên tĩnh như logo, icon
├── build.py                        # Kịch bản tự động đóng gói ứng dụng bằng PyInstaller
├── main.py                         # Điểm khởi chạy chính của ứng dụng (Entry Point)
├── PROJECT_PLAN.md                 # Tài liệu kế hoạch và đặc tả dự án
├── pytest.ini                      # Cấu hình cho Pytest
├── README.md                       # Giới thiệu tổng quan về dự án
├── requirements.txt                # Danh sách các thư viện Python cần thiết
├── run_tests.py                    # Kịch bản chạy toàn bộ Unit Tests
├── sync.bat                        # Kịch bản đồng bộ mã nguồn lên GitHub
├── USER_GUIDE.md                   # Hướng dẫn sử dụng chi tiết cho người dùng cuối
└── version.txt                     # File lưu trữ phiên bản hiện tại của ứng dụng
```

---

## Phần IV: Cấu Trúc Cơ Sở Dữ Liệu (Database Schema)

Hệ thống sử dụng các file cục bộ trong thư mục `data/` làm cơ sở dữ liệu chính.

### 1. Danh Sach SV.xlsx (Master Sinh Viên)
- **Khóa chính**: `Mã Sinh viên` (hoặc `Mã SV`, `MSV`).
- **Các cột dữ liệu**: `STT`, `Mã Sinh viên`, `Họ`, `Tên`, `Ngày sinh` (DD/MM/YYYY), `Số điện thoại`, `Email`,  `Số dư học phí` (Số nguyên, mặc định 0), `Trạng thái học tập`.

### 2. Quan Ly Lop Hoc {Năm}.xlsx (Master Lớp Học)
- **Tổ chức**: Mỗi Sheet đại diện cho một Đợt khai giảng (Wave).
- **Khóa chính**: `Mã Lớp`.
- **Các cột dữ liệu**: `STT`, `Mã Lớp`, `Niên Khóa`, `Tên Lớp`, `Địa điểm`, `Phòng học`, `Buổi học`, `Lịch học`, `Giờ học`, `Thời gian khai giảng`, `Ngày kết thúc khóa`, `SL Min`, `SL Max`, `SL Hiện tại`, `Trạng thái`.

### 3. form_links.json (Metadata & Configurations)
- **Mục đích**: Lưu trữ liên kết Google Form và danh sách lớp thuộc về từng Đợt.
- **Cấu trúc (JSON)**: `{"Niên khóa": {"Tên Đợt": {"form_link": "url", "sheet_link": "url", "classes": ["Mã lớp 1", "Mã lớp 2"]}}}`

---
*Ghi chú: Đánh dấu `[x]` vào các công việc đã hoàn thành để theo dõi tiến độ thực tế.*