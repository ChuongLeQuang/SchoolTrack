# AI_RULES.md (Python Full Version)

## 0. AI System Instructions / Nguyên tắc cốt lõi cho AI
- **Bắt buộc đọc tài liệu (Pre-computation reading)**:
  1. Luôn ưu tiên đọc và tuân thủ chặt chẽ file `AI_RULES.md` này trước khi phân tích logic hay viết bất kỳ dòng mã nào.
  2. Chủ động tìm và đọc các file hoạch định dự án cốt lõi (như `PLAN.md`, `PROJECT_PLAN.md`, hoặc `README.md` ở thư mục gốc) để hiểu rõ bối cảnh, luồng nghiệp vụ và tiến độ dự án.
  3. Đối với các file `.md` tài liệu khác, **chỉ đọc khi chúng thực sự liên quan** đến task đang xử lý (VD: tài liệu API, doc của module cụ thể) hoặc khi được người dùng yêu cầu rõ ràng, tránh việc đọc tràn lan làm phân tán ngữ cảnh.
- **Cập nhật tài liệu liên tục (Living Documentation)**: Kế hoạch (`PLAN.md`) không phải là tệp tĩnh. Bất cứ khi nào trong quá trình code phát sinh vấn đề mới, thay đổi luồng logic, hoặc thêm/bớt tính năng so với dự kiến ban đầu, AI **bắt buộc phải chủ động cập nhật lại file `PLAN.md`** để đảm bảo tài liệu luôn phản ánh đúng 100% thực tế của codebase.
- **Quy tắc lập kế hoạch (Planning & WBS Rules)**:
  1. **Chi tiết hóa tối đa (Granularity)**: Tuyệt đối không sử dụng các gạch đầu dòng chung chung trong `PLAN.md` (VD: "Khởi tạo dự án", "Xây dựng Models", "Làm UI"). Bắt buộc phải phân rã công việc thành WBS (Work Breakdown Structure) chi tiết đến mức liệt kê rõ từng tệp tin (file), lớp (class), hàm (function), API endpoint, và thậm chí là **từng trường dữ liệu (field/attribute), kiểu dữ liệu (dtype nếu cần)** cụ thể cần tạo.
  2. **Hoàn thiện Thiết kế (Design First)**: Tuyệt đối không bước sang Giai đoạn Viết mã (Phase 2 - Development) nếu Giai đoạn Thiết kế (Phase 1) chưa hoàn thiện 100%. Phase 1 phải bao phủ đầy đủ: Luồng dữ liệu (Data Flow), Cấu trúc Database, API Contract, UI/UX Mockup, và các kịch bản ngoại lệ/dị thường (Edge Cases/Error Handling).
  3. **Đối chiếu chéo (Cross-Audit)**: Trước khi chốt Giai đoạn Thiết kế (Phase 1) để chuyển sang Giai đoạn Viết mã (Phase 2), bắt buộc phải thực hiện đối chiếu chéo 1:1. Mỗi "Yêu cầu cốt lõi" phải có ít nhất một task tương ứng trong WBS. Bắt buộc lập "Báo cáo Đối chiếu chéo" dạng bảng lưu trực tiếp vào tệp `PLAN.md` làm bằng chứng nghiệm thu thiết kế.
  4. **Lập Lộ trình thi công (Execution Roadmap)**: Sau khi đã hoàn tất Phase 1 (Thiết kế) và Phase 2 (WBS chi tiết), bắt buộc phải lập "Lộ trình thi công (TDD Execution Sequence)". Lộ trình này phải tuân thủ nghiêm ngặt phương pháp "Outside-In TDD" (Phát triển từ ngoài vào trong: Giao thức/UI -> Lõi nghiệp vụ -> Lưu trữ) để đảm bảo sản phẩm luôn bám sát trải nghiệm người dùng.

## 1. Code Style & Convention
- **Language / Ngôn ngữ**: Python 3.x
- **Naming rules / Quy tắc đặt tên**:
  - **100% English / Bắt buộc tiếng Anh**: Tên biến, hàm, lớp và hằng số phải được đặt tên hoàn toàn bằng tiếng Anh có nghĩa (VD: `get_user_info` thay vì `lay_thong_tin_user`).
  - Variables & functions / Biến & hàm → `snake_case`
  - Classes / Lớp → `PascalCase`
  - Constants / Hằng số → `UPPER_CASE`
- **Imports / Thư viện**:
  - Standard libraries trước, third-party sau, local cuối cùng.
  - Dùng absolute import thay vì relative nếu có thể.
- **Type hints / Kiểu dữ liệu**:
  - Luôn khai báo type hints cho input/output.
  - Ví dụ:

```python
def calculate_area(radius: float) -> float:
    """
    EN: Calculate the area of a circle given its radius.
    VI: Tính diện tích hình tròn dựa trên bán kính.
    """
    return 3.14159 * radius * radius
```

- **Comments / Ghi chú**:
  - Dùng docstring cho module, class, function.
  - Bắt buộc viết comment/docstring song ngữ (EN + VI) ngắn gọn, rõ ràng.
  - Inline comment chỉ khi cần giải thích logic phức tạp.
- **Formatting / Định dạng**:
  - Theo chuẩn PEP8.
  - Dùng Black để auto-format (indent = 4 spaces).
  - Max line length = 88 ký tự.
  - **JSON Format**: Indent = 4 spaces, bắt buộc lưu encoding `UTF-8` (không escape ký tự Unicode). Naming convention cho JSON keys phải đồng nhất (ưu tiên `snake_case`).
- **Error handling / Xử lý lỗi**:
  - Luôn dùng `try/except` rõ ràng, không bắt lỗi chung chung (`except Exception`).
  - Comment giải thích lý do bắt lỗi.
  - **Custom Exceptions**: Bắt buộc tạo thư mục `exceptions/` (bên trong `src/`) để định nghĩa và chứa các lớp ngoại lệ tự tạo (Custom Exceptions). Tuyệt đối không nhồi nhét định nghĩa exception vào các file logic chính.
  - **Retry Mechanism / Cơ chế thử lại**: Bắt buộc áp dụng cơ chế Retry (thử lại khi thất bại) cho tất cả các hàm liên quan đến I/O (Network, Database, File) hoặc gọi API của bên thứ 3 nhằm đảm bảo tính ổn định khi gặp sự cố kết nối hoặc lỗi tạm thời (Transient Errors).

---

## 2. Project Structure
- Thư mục `src/` chứa toàn bộ logic chính.
- Thư mục `logs/` chứa các file nhật ký của ứng dụng (application logs, error logs).
- Thư mục `output/` chứa kết quả xuất ra của chương trình (ví dụ: file CSV, Excel báo cáo).
- Thư mục `data/` (hoặc `database/`) chứa các file CSDL cục bộ, file cấu hình gốc (ví dụ: `master_configs.json`, SQLite).
- **Frontend / Web Assets (Nếu dự án có giao diện Web)**:
  - Thư mục `static/` hoặc `public/` chứa tài nguyên tĩnh (images, css, js).
  - Thư mục `templates/` chứa các file giao diện HTML (nếu dùng Server-Side Rendering).
  - Nếu dùng framework Frontend độc lập (React/Vue/Angular), tách toàn bộ vào thư mục `frontend/` ở root.
- **Multi-module/Monorepo (Dự án lớn gồm nhiều chức năng/dự án nhỏ)**:
  - Tổ chức các chức năng/dự án nhỏ vào thư mục `apps/` hoặc `modules/` (ví dụ: `apps/module_a/`, `apps/module_b/`).
  - Mỗi dự án nhỏ bên trong phải tuân thủ chính xác cấu trúc thư mục độc lập (tự chứa `src/`, `tests/`,...).
  - Các utils, thư viện cốt lõi dùng chung cho nhiều dự án nhỏ nên đặt trong một thư mục `shared/` hoặc `core/` ở root.
- Không để file vượt quá **500 dòng** (ngoại trừ các file PLAN.md, PROJECT_PLAN.md, README.md, AI_RULES.md).
- Bên trong `src/`:
  - `models/` → định nghĩa dữ liệu, class, schema.
  - `services/` → xử lý nghiệp vụ, API call.
  - `utils/` → hàm tiện ích.
  - `controllers/` hoặc `views/` → xử lý request/response (nếu là web app).
  - `config/` → chứa các file thiết lập cấu hình ứng dụng.
- File Python đặt tên theo `snake_case.py`.
- **Quy chuẩn Đặt tên khi Tách File (Semantic Naming)**: Khi một file phình to và cần chia tách, tuyệt đối KHÔNG đặt tên chắp vá làm mất bối cảnh. Bắt buộc giữ nguyên cấu trúc thư mục phẳng hiện tại nhưng áp dụng công thức **[Tiền tố Miền nghiệp vụ]_[Tên chức năng]_[Hậu tố Vai trò].py** để các file cùng nghiệp vụ luôn đứng cạnh nhau theo bảng chữ cái.
  - *Tiền tố (Domain)*: `class_`, `student_`, `accounting_`...
  - *Hậu tố (Role)*: `_view.py` (Màn hình chính), `_tab.py` (Thẻ con), `_widget.py` (Thành phần UI), `_dialog.py` (Cửa sổ nổi).
  - *Ví dụ chuẩn*: `class_tab_planning.py`, `class_widget_links.py`.
- Thư mục `tests/` chứa unit test, file test đặt tên `test_<module>.py` tương ứng với file trong `src/`.

---

## 3. Flow & Architecture / Luồng & Kiến trúc
- **Development Workflow / Quy trình phát triển**:
  - **Bắt buộc thiết kế GUI (Giao diện người dùng) trước** khi bắt đầu code logic.
  - Khi phân tích dự án, AI/Dev phải phân tích dựa trên trải nghiệm/luồng UI (Mockup/Wireframe) để hiểu rõ mục tiêu, từ đó mới thiết kế Model, Service và Database tương ứng.
- **Layer separation / Phân tầng**:
  - Controller → Service → Model → Database.
  - Không gọi API trực tiếp trong UI hoặc controller, phải qua service.
- **Data flow / Luồng dữ liệu**:
  - Input → Validation → Business logic → Output.
  - Luôn validate dữ liệu trước khi xử lý.
- **Dependency management / Quản lý phụ thuộc**:
  - Dùng `requirements.txt` hoặc `pyproject.toml`.
  - Không hardcode version, dùng range hợp lý.
  - **Bắt buộc cập nhật (Auto-update dependencies)**: Bất cứ khi nào cài đặt hoặc import thêm một thư viện mới của bên thứ 3 vào mã nguồn, AI bắt buộc phải chủ động thêm thư viện đó (kèm theo phiên bản hoặc range hợp lý) vào file `requirements.txt` để đảm bảo dự án luôn chạy được trên môi trường mới.

---

## 4. Security & Performance
- **Security / Bảo mật**:
  - Không hardcode secret, dùng `.env` hoặc secret manager.
  - Luôn sanitize input để tránh SQL injection, XSS.
  - Không dùng `eval()` hoặc `exec()` trừ khi thật cần thiết.
- **Performance / Hiệu năng**:
  - Ưu tiên async/await cho I/O.
  - Tránh vòng lặp lồng nhau quá sâu.
  - Dùng caching khi cần.
- **Logging / Nhật ký**:
  - Dùng `logging` module thay vì `print`.
  - Log phải có level (INFO, WARNING, ERROR).

---

## 5. Testing & CI/CD
- **Testing / Kiểm thử**:
  - Dùng pytest.
  - **Bắt buộc**: Bất kỳ module hoặc function nào mới được tạo ra đều phải đi kèm với unit test tương ứng (Khuyến khích áp dụng TDD - Viết test trước, code sau).
  - Không chấp nhận code logic (Service, Utils, Model) mà không có test.
  - Coverage tổng thể và cho từng file tối thiểu ≥ 80%.
  - **Bắt buộc chạy test (Auto-run tests)**: Ngay sau khi hoàn thành việc viết code cho một tính năng (feature), AI phải tự động chạy thử test bằng lệnh shell (ví dụ: `pytest`) để xác nhận code hoạt động chính xác trước khi chuyển sang bước tiếp theo.
- **CI/CD / Tích hợp liên tục**:
  - Pipeline chạy lint + test trước khi merge.
  - Reject commit nếu vi phạm rule.
- **Example test / Ví dụ kiểm thử**:

```python
def test_calculate_area():
    """
    EN: Test circle area calculation with radius = 2.
    VI: Kiểm thử tính diện tích hình tròn với bán kính = 2.
    """
    assert calculate_area(2) == 12.56636
```

---

## 6. Documentation
- Mỗi module phải có README ngắn mô tả chức năng.
- Cập nhật tài liệu kiến trúc (nếu có) khi thêm module/flow mới.
- **Bảo toàn tài liệu (Content Preservation)**: Khi cập nhật tự động nội dung kiến trúc vào `README.md` (hoặc các file tài liệu khác), AI **bắt buộc** phải dựa vào các cờ đánh dấu (markers) như `<!-- ARCHITECTURE_START -->` và `<!-- ARCHITECTURE_END -->` để chỉ thay thế đúng phần nội dung ở giữa. Tuyệt đối không được ghi đè toàn bộ file làm mất các đoạn văn bản giải thích do người dùng tự viết.
- Tài liệu API (Swagger/Postman hoặc file Markdown) phải luôn được cập nhật đồng bộ với code.

---

## 7. Git & Version Control
- **Commit Message Convention / Chuẩn commit**:
  - Tuân thủ nghiêm ngặt [Conventional Commits](https://www.conventionalcommits.org/).
  - Cấu trúc: `<type>(<scope>): <subject>`
  - Các `type` bắt buộc: `feat` (tính năng mới), `fix` (sửa lỗi), `docs` (tài liệu), `style` (format, không đổi logic), `refactor` (tối ưu code), `test` (kiểm thử), `chore` (cấu hình, tool, build).
  - Tiêu đề (subject) ngắn gọn, **không quá 72 ký tự**, viết rõ ràng (có thể dùng EN/VI nhưng phải thống nhất).
- **Branch Naming / Đặt tên nhánh**:
  - `feature/<tên-chức-năng>` (ví dụ: `feature/export-excel`)
  - `bugfix/<tên-lỗi>` (ví dụ: `bugfix/fix-null-pointer`)
  - `hotfix/<tên-lỗi-nghiêm-trọng>` cho các bản vá khẩn cấp cần đưa lên production ngay.
- **Pull Request / Merge Request**:
  - PR phải có mô tả rõ ràng (What, Why, How).
  - Khuyến khích squash các commit "rác" (như "fix typo", "update again") thành 1 commit có ý nghĩa trước khi merge.

---

## 8. Build & Packaging / Đóng gói ứng dụng
- **Module Recognition / Nhận diện Module**:
  - Bắt buộc: Mọi thư mục chứa mã nguồn Python (như `src/`, `views/`, `services/`...) đều phải chứa file `__init__.py` (kể cả file trống). Điều này giúp Python và các công cụ đóng gói (PyInstaller) nhận diện chính xác đó là một Package hợp lệ.
- **Path Resolution / Cấu hình Đường dẫn**:
  - Không lạm dụng hoặc phụ thuộc hoàn toàn vào biến `__file__` để lấy đường dẫn gốc. Khi ứng dụng được đóng gói thành file thực thi (ví dụ: `.exe`), `__file__` sẽ không còn trỏ đúng cấu trúc thư mục vật lý.
  - Đối với các file tài nguyên tĩnh (assets, configs, templates), luôn sử dụng cơ chế kiểm tra môi trường linh hoạt (VD: kiểm tra `getattr(sys, 'frozen', False)` để lấy `sys._MEIPASS` cho PyInstaller).
  - **Xử lý tệp tĩnh (Static Assets)**: Đối với các tệp tĩnh (ảnh, icon, configs), tuyệt đối KHÔNG gọi trực tiếp bằng đường dẫn tương đối (VD: `open("assets/icon.png")`). Luôn dùng `os.path.join(project_root, "assets", "icon.png")` với `project_root` đã được phân giải an toàn qua cơ chế `sys._MEIPASS`.
- **System Path Manipulation / Can thiệp sys.path**:
  - **Tuyệt đối KHÔNG sử dụng `sys.path.insert(0, ...)` hoặc `sys.path.append(...)` để hack đường dẫn import.** Hành động này phá vỡ cơ chế resolve module mặc định của Python và PyInstaller, là nguyên nhân chính gây ra lỗi `ModuleNotFoundError: No module named 'src'`.
- **Execution Context / Ngữ cảnh thực thi (Tránh lỗi Not module src)**:
  - **Bắt buộc**: Các file Entry Point (như `main.py`, `app.py`, `gui_init_project.py`) phải luôn được đặt ở **thư mục gốc (root)** của dự án.
  - Khi build PyInstaller, **chỉ** được truyền vào file Entry Point ở root (VD: `pyinstaller gui_init_project.py`), tuyệt đối không truyền file nằm trong `src/`.
  - Khi test/run code thủ công, nếu cần chạy một file sâu bên trong `src/`, phải đứng ở thư mục gốc và dùng cờ `-m` (VD: `python -m src.views.main_window`). Tuyệt đối KHÔNG chạy trực tiếp `python src/views/main_window.py`.
- **Build Configuration / Cấu hình đóng gói**:
  - **Bắt buộc**: Phải luôn tạo một kịch bản đóng gói chuyên dụng (ví dụ: `build.py`, `Makefile`, hoặc file `.spec` của PyInstaller) để quản lý quá trình build thay vì gõ lệnh CLI thủ công.
  - **Bảo trì và Đồng bộ**: Tệp kịch bản đóng gói này phải luôn được kiểm tra và cập nhật đồng bộ ngay lập tức mỗi khi có thay đổi trong mã nguồn ảnh hưởng đến quá trình đóng gói (ví dụ: thêm tệp tài nguyên tĩnh `assets`, bổ sung thư viện phụ thuộc ẩn, hoặc thay đổi tên Entry Point).
  - **Clean Build / Dọn dẹp trước khi đóng gói**: Trước khi thực thi lệnh PyInstaller, kịch bản build bắt buộc phải quét và xóa sạch các tệp/thư mục tạm (như `__pycache__`, thư mục `build/`, `dist/`, hoặc các file `.log` cũ) để đảm bảo tệp thực thi luôn là phiên bản tinh gọn nhất và không bị đóng gói nhầm mã nguồn cũ.

---

## 9. Copyright & Licensing / Bản quyền & Giấy phép
- **License File**: Bất kỳ dự án hoặc module mã nguồn mở nào được khởi tạo cũng phải đi kèm một tệp giấy phép rõ ràng ở thư mục gốc.
- **Copyright Header**: Đối với các dự án nội bộ doanh nghiệp hoặc dự án thương mại, các file mã nguồn quan trọng nên có một đoạn chú thích bản quyền ở phần đầu của file.
- **Tuân thủ Dependency**: Khi sử dụng thư viện bên thứ 3 (trong `requirements.txt`), phải đảm bảo quy định sử dụng của chúng không xung đột với định hướng của dự án gốc.

---

## 10. Blood Rules / Nguyên tắc xương máu từ thực tiễn
Những nguyên tắc này được đúc kết từ các sự cố nghiêm trọng (treo máy, sập luồng, phình to kiến trúc) trong quá trình phát triển thực tế, bắt buộc AI/Dev phải kiểm tra trước khi viết code:

- **Xử lý I/O Phòng thủ & Kiểm thử Dữ liệu Bẩn (Defensive I/O & Dirty Testing)**: 
  - *Nguyên tắc*: Không bao giờ tin tưởng tuyệt đối vào ranh giới dữ liệu do thư viện bên thứ 3 báo cáo (VD: `openpyxl.max_row` có thể lên tới 1 triệu dòng do lỗi format của người dùng). Bắt buộc phải tự viết các cơ chế "Cắt tỉa" (Trim) hoặc "Ngắt tự động" (Break - ngắt sau 50 dòng/20 cột trống). 
  - *Kiểm thử*: Các bài Unit Test cho Service xử lý dữ liệu bắt buộc phải có kịch bản test "Dữ liệu rác" để kiểm chứng khả năng chịu đựng của hệ thống.
- **Tối ưu hóa Cập nhật UI Hàng loạt (Bulk Update Optimization)**: 
  - *Nguyên tắc*: Khi thêm/xóa/sửa số lượng lớn phần tử trên giao diện (`QTableWidget`, `QListWidget`), **bắt buộc** phải khóa luồng render (`setUpdatesEnabled(False)`), dọn dẹp bộ nhớ đệm (`setRowCount(0)`), bơm dữ liệu, sau đó mới mở khóa render. Điều này ngăn chặn lỗi "ngạt thở" UI do tính năng tự động co giãn (`ResizeToContents`) bị kích hoạt hàng triệu phép tính thừa.
- **Ranh giới Nghiệp vụ Nghiêm ngặt (Strict Domain Boundaries)**: 
  - *Nguyên tắc*: Tuyệt đối tuân thủ Kiến trúc Phân tầng. Không được phép nhồi nhét UI hoặc Logic của module này (VD: Làm giàu dữ liệu Sinh viên) vào bên trong module khác (VD: Quản lý Lớp học). Nếu một tệp vượt quá 500 dòng, bắt buộc dừng lại để chia tách (Refactor).
- **Rải bẫy Đo lường Hiệu năng (Performance Trapping)**: 
  - *Nguyên tắc*: Đối với các tác vụ "nặng đô" (như đọc/ghi Excel lớn, gọi API), bắt buộc phải chèn các hàm ghi log thời gian thực (timestamps) tại các điểm nút (Milestones). Đề phòng trường hợp ứng dụng "chết lâm sàng" không văng Exception (Silent Crash), dòng log cuối cùng sẽ ngay lập tức chỉ điểm rò rỉ hiệu năng.
- **Chống Lạm dụng Mocking & Ưu tiên Kiểm thử Tích hợp (Anti-Mocking Abuse & Integration Testing)**:
  - *Hạn chế Mock File System*: Khi kiểm thử các luồng Đọc/Ghi dữ liệu (Excel, JSON), hạn chế tối đa việc dùng `@patch` để làm giả thư viện. Ưu tiên dùng `tmp_path` của `pytest` để tạo file vật lý thật, nhằm kiểm chứng tính xác thực 100% của thư viện bên dưới (VD: `openpyxl`).
  - *Bật Strict Mock*: Đối với các thành phần bắt buộc phải làm giả (API mạng, UI Components), lệnh `@patch` **bắt buộc** phải đi kèm tham số `autospec=True`. Cơ chế này ép đối tượng giả phải có cấu trúc y hệt đối tượng thật, dập tắt hoàn toàn rủi ro "gọi sai tên hàm (AttributeError) nhưng test vẫn báo Pass".

---

## 11. AI Output Generation & Diff Discipline / Kỷ luật sinh mã và vá lỗi
Để tránh các lỗi khi áp dụng mã nguồn (patching/merging) do IDE từ chối hoặc bị tràn giới hạn token, AI bắt buộc tuân thủ:

- **Tuyệt đối không viết tắt trong Diff (No Elision)**: Trong các khối mã `diff`, tuyệt đối không sử dụng `...`, `pass`, hoặc comment đại diện để thay thế cho code hiện có chưa được sửa đổi. Phải cung cấp bối cảnh (context) một cách rõ ràng và liền mạch.
- **Sao chép nguyên trạng bối cảnh (Exact Context Matching)**: Các dòng code không thay đổi (context lines) và các dòng bị xóa (bắt đầu bằng dấu `-`) phải được sao chép **chính xác 100%** từ file gốc (bao gồm cả thụt lề, khoảng trắng). Không tự ý sửa lỗi chính tả hay định dạng ở các dòng bối cảnh này.
- **Gộp khối vá (Single Diff Block per File)**: Nếu cần thay đổi nhiều vị trí trong cùng một tệp, bắt buộc phải gộp chúng vào **một khối `diff` duy nhất** (sử dụng nhiều phần `@@ ... @@`), tuyệt đối không tách ra thành nhiều khối diff riêng biệt cho cùng một tệp.
- **Phân rã Output (Output Chunking)**: Nếu một tính năng yêu cầu tạo mới/sửa đổi từ 3 file trở lên, HOẶC tổng số dòng code thay đổi vượt quá 150 dòng, AI **tuyệt đối không được nhồi nhét tất cả vào một lần trả lời**. Phải chủ động chia nhỏ việc giao code thành nhiều đợt (Ví dụ: *"Phần 1: Models & Utils. Lưu lại và gõ 'Tiếp' để nhận Phần 2"*).
- **Giới hạn bối cảnh (Strict Context Limit)**: Khi sử dụng chuẩn `diff`, chỉ được in ra tối đa **3 đến 5 dòng code cũ (context lines)** ở trên và dưới đoạn mã cần sửa. Tuyệt đối không in lại toàn bộ các hàm không liên quan hoặc cả một file dài chỉ để sửa một vài chỗ, nhằm tiết kiệm bộ nhớ output token.
