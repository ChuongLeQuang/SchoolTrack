# 📖 Hướng Dẫn Sử Dụng Phần Mềm SchoolTrack

Tài liệu này cung cấp hướng dẫn chi tiết về cách sử dụng các tính năng của phần mềm SchoolTrack, giúp bạn quản lý trung tâm một cách hiệu quả và chính xác.

## 1. Giới thiệu

**SchoolTrack** là công cụ giúp số hóa toàn bộ quy trình quản lý lớp học, từ việc lên kế hoạch, thu thập đăng ký của sinh viên, đối chiếu học phí với kế toán, cho đến việc ra quyết định mở hoặc hủy lớp.

## 2. Giao diện chính

Giao diện chính của phần mềm bao gồm 2 khu vực:

1.  **Thanh điều hướng (Sidebar) bên trái**: Chứa các menu để chuyển đổi giữa các màn hình chức năng chính:
    *   `📊 Dashboard`: (Sắp ra mắt) Cung cấp cái nhìn tổng quan về hoạt động của trung tâm.
    *   `🧑‍🎓 Quản lý Sinh viên`: Quản lý danh sách và thông tin của tất cả sinh viên.
    *   `🏫 Quản lý Lớp học`: Chức năng cốt lõi, quản lý toàn bộ vòng đời của một lớp học.
2.  **Khung nội dung bên phải**: Hiển thị chi tiết nội dung của chức năng được chọn từ Sidebar.

---

## 3. Quản lý Sinh viên

Màn hình này là nơi lưu trữ cơ sở dữ liệu "gốc" về toàn bộ sinh viên của trung tâm. Dữ liệu được lưu trong file `apps/main_app/data/Danh Sach SV.xlsx`.

### 3.1. Xem, Tìm kiếm và Lọc

*   **Tải lại dữ liệu**: Nhấn nút `🔄 Tải lại Dữ liệu` để cập nhật danh sách mới nhất từ file Excel.
*   **Tìm kiếm**: Gõ vào ô `🔍 Tìm theo MSV, Họ, Tên...` để tìm kiếm nhanh sinh viên. Bảng sẽ tự động lọc kết quả ngay khi bạn gõ.
*   **Lọc theo trạng thái**: Chọn một trạng thái từ hộp thả xuống (ví dụ: "Đang học", "Nghỉ học") để xem danh sách sinh viên tương ứng.

### 3.2. Thêm, Sửa, Xóa Sinh viên

*   **Thêm mới**:
    1.  Nhấn nút `➕ Thêm`.
    2.  Hệ thống sẽ tự động gợi ý một Mã Sinh viên (MSV) mới.
    3.  Điền đầy đủ thông tin và nhấn `💾 Lưu`.
*   **Sửa thông tin**:
    1.  Click chọn một sinh viên trong bảng.
    2.  Nhấn nút `✏️ Sửa` (hoặc click đúp vào dòng đó).
    3.  Thay đổi thông tin cần thiết và nhấn `💾 Lưu`.
    > **Lưu ý**: Mã Sinh viên (MSV) là khóa chính, không thể thay đổi khi sửa.
*   **Xóa sinh viên**:
    1.  Click chọn một sinh viên trong bảng.
    2.  Nhấn nút `🗑️ Xóa`.
    3.  Xác nhận hành động trong hộp thoại hiện ra.

> **⚠️ CẢNH BÁO QUAN TRỌNG**: Nếu file `Danh Sach SV.xlsx` đang được mở bởi một chương trình khác (như Microsoft Excel), bạn sẽ không thể Lưu hoặc Xóa. Vui lòng đóng file Excel trước khi thực hiện các thao tác này.

### 3.3. Lưu ý quan trọng về "Số dư học phí"

Cột "Số dư học phí" trên bảng Quản lý Sinh viên là một tính năng quan trọng nhưng cần được hiểu đúng để tránh nhầm lẫn:

*   **Không phải dữ liệu thời gian thực**: Số liệu này **KHÔNG** được cập nhật ngay lập tức mỗi khi có giao dịch. Nó là **ảnh chụp (snapshot)** tình hình công nợ của sinh viên tại **thời điểm đối chiếu gần nhất** với bộ phận Kế toán.
*   **Nguồn dữ liệu**: Dữ liệu công nợ được lấy từ file Excel do **bộ phận Kế toán** cung cấp. SchoolTrack chỉ đóng vai trò hiển thị, không tự tính toán hay phát sinh công nợ.
*   **Cập nhật khi nào?**: Số dư này sẽ được cập nhật hàng loạt khi bạn thực hiện chức năng ở **Giai đoạn 2: Đối chiếu Kế toán** trong màn hình Quản lý Lớp học.
*   **Khi có sai lệch**: Mọi thắc mắc hoặc sai lệch về số dư học phí cần được xác minh và xử lý trực tiếp với bộ phận Kế toán, vì họ là nguồn dữ liệu gốc.

---

## 4. Quản lý Lớp học (Quy trình cốt lõi)

Đây là màn hình phức tạp và mạnh mẽ nhất, được chia thành 3 giai đoạn tương ứng với 3 Tab con trong menu.

### 4.1. Tổng quan về Niên khóa và Đợt

*   **Niên khóa**: Là một năm học (ví dụ: `2025-2026`). Mỗi niên khóa tương ứng với một file Excel `Quan Ly Lop Hoc {năm}.xlsx`. Bạn có thể tạo niên khóa mới bằng nút `➕ Tạo Niên Khóa Mới`.
*   **Đợt**: Là một đợt tuyển sinh/khai giảng trong niên khóa (ví dụ: "Đợt 1", "Tháng 10"). Mỗi đợt tương ứng với một **Sheet** trong file Excel của niên khóa đó. Bạn có thể `➕ Tạo`, `✏️ Sửa Tên`, `🗑️ Xóa` các đợt.
    *   *Tính năng an toàn*: Hệ thống sẽ tự động loại bỏ các dấu cách thừa khi bạn nhập tên Đợt để tránh tình trạng tạo nhầm các Đợt trùng nhau (VD: "Đợt 1" và "Đợt   1").
*   **Tùy chọn "Tất cả"**: Là chế độ xem tổng hợp toàn bộ lớp học của tất cả các đợt. **Lưu ý:** Để bảo vệ an toàn dữ liệu, khi bạn đang chọn xem "Tất cả", các nút thao tác làm thay đổi dữ liệu (Thêm, Sửa, Xóa, Cập nhật...) sẽ bị làm mờ/khóa. Bạn cần chọn một Đợt cụ thể để có thể thực hiện thay đổi.

### 4.2. Giai đoạn 1: Lên Kế hoạch Dự kiến

Đây là nơi bạn tạo ra các "rổ" để chuẩn bị gom sinh viên đăng ký.

#### Tạo Lớp dự kiến (Rổ đăng ký)

1.  Chọn **Niên khóa** và **Đợt** bạn muốn làm việc.
2.  Nhấn nút `➕ Thêm`.
3.  Trong hộp thoại hiện ra:
    *   **Chọn Cấp độ**: Chọn một mẫu lớp có sẵn (ví dụ: "NE - Tiếng Anh Level 1"). Các thông tin như Tên lớp, SL Min/Max, Ca học... sẽ được tự động điền.
    *   **Tháng Khai giảng**: Chọn tháng/năm dự kiến.
    *   Hệ thống sẽ tự động sinh ra một **Mã Lớp 10 ký tự** (ví dụ: `LNH0825NEA`). Mã này là duy nhất và không thể sửa.
4.  Kiểm tra lại các thông tin và nhấn `💾 Lưu`.

#### Cấu hình Link và Copy cho Google Form

Mỗi **Đợt** sẽ được gắn với một cặp link Google Form riêng.

1.  **Nhập link**: Dán link Google Form (gửi cho SV) và link Google Sheet (kết quả trả về) vào 2 ô tương ứng.
2.  **Lưu cấu hình**: Nhấn `💾 Lưu Cấu Hình Link` để lưu lại.
3.  **Copy cho Form**:
    *   Tick vào các ô `Chọn` ở đầu mỗi dòng lớp học bạn muốn đưa lên Form.
    *   Nhấn nút `📋 Copy cho Google Form`.
    *   Mở Google Form của bạn, đi đến câu hỏi trắc nghiệm chọn lớp và nhấn `Ctrl+V` để dán toàn bộ danh sách vào.

#### 🪄 Tự động tạo Form bằng API (Khuyên dùng)

Thay vì phải làm thủ công, bạn có thể cấu hình để phần mềm tự động nhân bản Form mẫu và chèn danh sách lớp học giúp bạn.

**Bước 1: Chuẩn bị Form Mẫu trên Google Drive**
1. Mở Google Drive của trung tâm, tạo một Google Biểu mẫu (Form) mới.
2. Trang trí form thật đẹp (thêm logo, màu sắc) và thiết lập các câu hỏi thu thập thông tin cơ bản (Họ tên, Mã SV, SĐT, Email...).
3. **Lưu ý:** KHÔNG tạo câu hỏi chọn lớp học ở đây. Phần mềm sẽ tự động gắn nó vào sau.
4. Copy **ID của Form Mẫu**. (ID là đoạn mã nằm giữa `/d/` và `/edit` trên thanh địa chỉ trang web của trình duyệt).

**Bước 2: Cài đặt "Nhân viên ảo" (Google Apps Script)**
1. Truy cập vào `script.google.com` và nhấn **Dự án mới** (New Project).
2. Xóa hết mã cũ và dán đoạn mã (script) mà đội ngũ kỹ thuật cung cấp vào đó. Nhấn nút **Lưu** (Save).
2. Xóa hết mã cũ và dán đoạn mã (script) dưới đây vào đó. Nhấn nút **Lưu** (Save).

   ```javascript
   function doPost(e) {
     try {
       var payload = JSON.parse(e.postData.contents);
       var secret = payload.secret;
       var waveName = payload.wave_name;
       var classes = payload.classes;
       var templateId = payload.template_id;

       // 1. Kiểm tra mật khẩu (Bạn có thể đổi mật khẩu này)
       if (secret !== "mat_khau_cua_trung_tam_123") {
         return ContentService.createTextOutput(JSON.stringify({status: "error", message: "Sai Mật khẩu bảo mật!"})).setMimeType(ContentService.MimeType.JSON);
       }

       // 2. Tạo file Excel (Spreadsheet) mới để lưu ai đăng ký
       var newSheet = SpreadsheetApp.create("Kết quả Đăng ký - " + waveName);

       // 3. Nhân bản cái Form Mẫu bạn đã làm ở Bước 1
       var templateFile = DriveApp.getFileById(templateId);
       var newFile = templateFile.makeCopy("Đăng ký Lớp học - " + waveName);
       var newForm = FormApp.openById(newFile.getId());
       
       // 4. Móc nối Form mới với Sheet mới
       newForm.setDestination(FormApp.DestinationType.SPREADSHEET, newSheet.getId());
       
       // 5. Tự động chèn thêm câu hỏi "Chọn lớp" vào cuối Form
       var item = newForm.addMultipleChoiceItem();
       item.setTitle("Vui lòng chọn Lớp học bạn muốn đăng ký:");
       item.setChoiceValues(classes);
       item.setRequired(true);

       // 6. Báo cáo về cho phần mềm SchoolTrack biết đã làm xong
       return ContentService.createTextOutput(JSON.stringify({
         status: "success", 
         form_url: newForm.getPublishedUrl(), 
         sheet_url: newSheet.getUrl()
       })).setMimeType(ContentService.MimeType.JSON);

     } catch (error) {
       return ContentService.createTextOutput(JSON.stringify({status: "error", message: error.toString()})).setMimeType(ContentService.MimeType.JSON);
     }
   }
   ```
3. Nhấn nút màu xanh **Triển khai** (Deploy) ở góc phải -> Chọn **Triển khai mới** (New deployment).
4. Ở mục Chọn loại (Select type), chọn hình bánh răng cưa -> **Ứng dụng Web** (Web app).
5. Thiết lập chính xác như sau:
   * Thực thi dưới dạng (Execute as): **Tôi** (Me).
   * Người có quyền truy cập (Who has access): **Bất kỳ ai** (Anyone). *(Bắt buộc)*
6. Nhấn **Triển khai** (Deploy). Nếu Google hỏi quyền, hãy cấp quyền cho nó.
7. Copy lại đường link **Web App URL** dài loằng ngoằng vừa hiện ra.

**Bước 3: Cấu hình trên phần mềm SchoolTrack**
1. Mở SchoolTrack, vào Tab *Quản lý Lớp học*.
2. Nhấn nút `⚙️ Cấu hình API Google Form`.
3. Dán **Web App URL** (lấy ở bước 2), **Form Mẫu ID** (lấy ở bước 1) và **Mật khẩu** (Secret Token) vào. Nhấn Lưu.

**Bước 4: Sử dụng**
1. Tick chọn các lớp dự kiến bạn muốn mở đăng ký trên bảng.
2. Nhấn nút `🪄 Tự động tạo Form`. Chờ khoảng 10 giây, phần mềm sẽ báo thành công và tự động điền 2 đường link mới vào ô.

> ⚠️ **LƯU Ý QUAN TRỌNG (Các bước làm thủ công bắt buộc):**
> Do chính sách bảo mật khắt khe của Google (đặc biệt trên các tài khoản cá nhân và tài khoản cấp phát nội bộ), tính năng API chưa thể tự động mở khóa 100%. **Sau khi tạo form thành công, bạn BẮT BUỘC phải làm 2 việc sau:**
> 
> 1. **Mở công khai Form:** 
>    - Nhấn nút `🌐 Mở Form` trên phần mềm.
>    - (Nếu dùng tài khoản tổ chức) Chuyển sang tab **Cài đặt** (Settings), kéo xuống phần Câu trả lời, TẮT mục *"Hạn chế ở người dùng trong tổ chức"*. Nếu không tắt, sinh viên sẽ không thể điền form.
> 2. **Chia sẻ Sheet (Cho phép phần mềm tải về):**
>    - Nhấn nút `🌐 Mở Sheet` trên phần mềm.
>    - Nhấn nút **Chia sẻ** (Share) màu xanh ở góc phải trên cùng.
>    - Đổi Quyền truy cập chung thành **Bất kỳ ai có đường liên kết** (Anyone with the link). Nếu không làm bước này, khi bạn bấm "📥 Tải File", phần mềm sẽ báo lỗi file bị khóa.

#### Cập nhật Số lượng Đăng ký (Tính năng quan trọng)

Sau khi sinh viên điền Form, bạn cần cập nhật số lượng đăng ký thực tế vào phần mềm.

1.  **Tải file Excel từ Google Sheet**: Mở link Google Sheet kết quả, vào `Tệp > Tải xuống > Microsoft Excel (.xlsx)`.
2.  **Chọn Chế độ xử lý MSV sai**:
    *   Đây là bước quan trọng nhất, quyết định cách phần mềm xử lý các trường hợp sinh viên gõ nhầm Mã Sinh viên.
    *   Bạn có 3 lựa chọn trong hộp thả xuống:
        *   **1. Lọc cứng (Mặc định)**: An toàn nhất. Chỉ đếm những lượt đăng ký có MSV **khớp 100%** với `Danh Sach SV.xlsx`. Mọi lượt đăng ký có MSV sai sẽ bị **bỏ qua âm thầm**.
        *   **2. Cảnh báo**: Tương tự Lọc cứng, nhưng sau khi cập nhật sẽ **hiện một bảng thông báo** liệt kê những sinh viên đã nhập sai MSV. Giúp bạn biết và liên hệ họ để sửa.
        *   **3. Thông minh**: Cố gắng **tự động sửa lỗi**. Nếu MSV sai, hệ thống sẽ thử tìm sinh viên đó trong `Danh Sach SV.xlsx` bằng **Email** hoặc **Số điện thoại**. Nếu tìm thấy, nó sẽ tự sửa và tính lượt đăng ký đó là hợp lệ. Nếu vẫn không tìm thấy, nó sẽ báo lỗi như chế độ "Cảnh báo".
3.  **Nhấn nút `📥 Cập nhật SL Đăng ký`**.
4.  **Chọn file Excel** bạn vừa tải về ở bước 1.

Hệ thống sẽ tự động đọc file, khử các lượt đăng ký trùng lặp (chỉ lấy lần nộp form cuối cùng của mỗi sinh viên), xử lý MSV ảo theo chế độ bạn chọn, và cập nhật số lượng vào cột `Đăng Ký` trên bảng.

### 4.3. Giai đoạn 2: Đối chiếu Kế toán

Sau khi sinh viên đăng ký và đi đóng tiền, bộ phận Kế toán sẽ có một file Excel ghi nhận các giao dịch. Tab này giúp bạn tự động hóa việc đối chiếu giữa danh sách đăng ký và danh sách đã đóng tiền, đồng thời cập nhật công nợ cho từng sinh viên.

**Đây chính là quy trình sẽ cập nhật dữ liệu cho cột "Số dư học phí" ở màn hình Quản lý Sinh viên.**

1.  Nhấn nút `📂 Chọn & Đối chiếu File Kế toán`.
2.  Chọn file Excel do Kế toán cung cấp.
3.  Hệ thống sẽ xử lý và hiển thị kết quả trên bảng:
    *   **Hợp lệ**: Sinh viên vừa có trong danh sách đăng ký, vừa có trong danh sách đóng tiền.
    *   **Lệch khớp**: Sinh viên có đóng tiền nhưng MSV hoặc Mã lớp không khớp với dữ liệu gốc.
    *   **Chưa đóng tiền**: Sinh viên có đăng ký nhưng không có tên trong file của Kế toán.

### 4.4. Giai đoạn 3: Chốt Lớp & Phân bổ

Dựa trên số lượng sinh viên đăng ký hợp lệ ở các giai đoạn trước, bạn sẽ vào đây để ra quyết định cuối cùng.

*   **Chốt Mở lớp**: Với những lớp có cột `Đăng Ký` ≥ `SL Min`.
*   **Hủy lớp**: Với những lớp không đủ số lượng.
*   **Phân bổ**: Gán phòng học, giáo viên cho các lớp được mở.

*(Lưu ý: Giao diện và tính năng chi tiết cho giai đoạn này sẽ được phát triển trong các phiên bản sau)*

---

## 5. Các câu hỏi thường gặp (FAQ)

*   **Tại sao tôi không Lưu/Sửa/Xóa được dữ liệu?**
    *   Rất có thể file Excel (`Danh Sach SV.xlsx` hoặc `Quan Ly Lop Hoc...xlsx`) đang được mở ở một nơi khác. Hãy đảm bảo bạn đã đóng tất cả các file Excel liên quan trước khi thao tác.
*   **Làm thế nào để chế độ "Thông minh" hoạt động chính xác?**
    *   Bạn cần đảm bảo file `Danh Sach SV.xlsx` có đầy đủ và chính xác cột `Email` và `Số điện thoại`. Đồng thời, Google Form của bạn cũng phải thu thập 2 thông tin này.
*   **Tôi có thể sửa Mã Lớp dự kiến (10 ký tự) không?**
    *   Không. Mã lớp dự kiến được sinh tự động và là duy nhất để đảm bảo tính toàn vẹn dữ liệu khi liên kết với Google Form. Nếu muốn thay đổi, bạn cần xóa lớp cũ và tạo lại lớp mới.