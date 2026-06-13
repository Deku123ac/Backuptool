# Lộc Phát Design Backup Pro

Tool backup portable cho Windows, có giao diện Tiếng Việt / English, hỗ trợ backup theo lịch, nén ZIP, kiểm tra SHA-256 và tạo manifest cho mỗi bản backup.

## Tải về

1. Mở repo: https://github.com/Deku123ac/Backuptool
2. Vào file `dist/BackupToolPro-portable.zip`
3. Bấm `Download raw file` hoặc `View raw` để tải ZIP
4. Giải nén ZIP
5. Mở `Open_BackupToolPro.bat`

## Cách dùng nhanh

1. Mở `Open_BackupToolPro.bat`
2. App mở ở trang `Cấu hình đã lưu`
3. Nếu đã có cấu hình cũ, tick chọn cấu hình rồi bấm `Chỉnh sửa cấu hình` hoặc `Chạy cấu hình này`
4. Khi chỉnh sửa cấu hình cũ, bấm `Hoàn tất` sẽ ghi đè cấu hình đó, không sinh thêm dòng mới
5. Nếu muốn tạo cấu hình mới, bấm `Tạo cấu hình mới`
6. Bước `Dữ liệu`: thêm file/folder cần backup
7. Bước `Nơi lưu`: chọn folder lưu backup
8. Bước `Lịch`: chọn ngày bắt đầu, lịch, ngày và giờ backup
9. Bước `Chạy backup`: bấm `Kiểm tra`, `Backup ngay` hoặc `Cài lịch`

App tự lưu tối đa 20 cấu hình gần nhất. Các cấu hình này chỉ là đường dẫn, lịch và tuỳ chọn, thường chỉ vài KB, không ngốn dung lượng.

Gói hiện tại là bản source-safe không đóng gói EXE để giảm cảnh báo Windows Defender. Máy cần có Python 3.12 trở lên. Nếu thiếu thư viện, launcher sẽ tự cài theo `requirements.txt`. Launcher dùng `pythonw` nên không bật cửa sổ console đen.

Khi backup, app copy từng file và cập nhật phần trăm liên tục. Giao diện chỉ hiển thị thống kê nhẹ; quét sâu chỉ chạy khi bấm `Kiểm tra`, `Backup ngay`, hoặc `Cài lịch`.

Để tránh lỗi đường dẫn quá dài như `.venv\Lib\site-packages\...\__pycache__`, app tự bỏ qua các folder kỹ thuật/cache: `.venv`, `venv`, `__pycache__`, `.git`, `node_modules`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`.

Lịch `Mỗi ngày` có `Ngày bắt đầu`; Windows chỉ chạy tự động từ ngày đó trở đi. Lịch `Mỗi ngày` không dùng checkbox ngày. Checkbox ngày chỉ dùng cho chế độ `Tùy chọn ngày`.

Mặc định app giữ 3 bản backup gần nhất. Bạn có thể tăng/giảm số này ở bước `Chạy backup`.

`Hoàn tất` chỉ lưu cấu hình/lịch và quay về danh sách cấu hình đã lưu. Nó không quét file, không copy và không tạo backup mới. Backup thật chỉ chạy khi bấm `Backup ngay` hoặc tới đúng giờ lịch Windows đã cài.

## Các nút trong app

- `Kiểm tra`: kiểm tra cấu hình trước khi chạy, gồm dữ liệu nguồn có tồn tại không, nơi lưu có hợp lệ không, quyền đọc/ghi và dung lượng còn đủ không.
- `Cài lịch`: tạo lịch tự động bằng Windows Task Scheduler. Sau khi cài, Windows tự chạy backup theo giờ đã chọn.
- `Backup ngay`: chạy backup ngay tại thời điểm hiện tại.
- `Chỉnh sửa cấu hình`: nạp lại cấu hình cũ để chỉnh sửa hoặc cài lịch lại. Khi bấm `Hoàn tất`, app ghi đè cấu hình đang chỉnh.
- `Chạy cấu hình này`: nạp cấu hình cũ và backup ngay.
- `Gỡ lịch tự động`: xoá lịch backup tự động khỏi Windows Task Scheduler.
- `Mở log`: mở file log để xem lịch sử backup và lỗi nếu có.

## Chế độ lịch

- `Mỗi ngày`: backup mỗi ngày
- `Mỗi tuần`: backup mỗi tuần vào một ngày đã chọn
- `Tuỳ chọn`: backup vào nhiều ngày tuỳ chọn, ví dụ Thứ 2, Thứ 3, Thứ 4

## Cơ chế an toàn

Tool chỉ báo thành công khi:

- Tất cả file/folder nguồn còn tồn tại
- Copy đầy đủ dữ liệu
- Verify từng file bằng SHA-256 thành công
- File ZIP tạo xong và kiểm tra không lỗi. Nếu đường dẫn bên trong ZIP quá dài khiến Windows Explorer dễ báo ZIP invalid, app tự giữ bản backup dạng folder đã verify thay vì tạo ZIP hỏng.
- Manifest được tạo thành công

Nếu gặp lỗi:

- Tool báo thất bại
- Không tạo backup giả
- Không xoá các bản backup cũ
- Chi tiết lỗi nằm trong `backup_log.txt`

## Lỗi Access is denied

Nếu Windows báo `Access is denied`, thường là do file/folder đang bị khoá quyền, đang được phần mềm khác dùng, hoặc cần quyền Administrator.

Cách xử lý:

1. Đóng phần mềm đang mở file/folder đó
2. Mở lại app bằng `Run as administrator`
3. Nếu vẫn bị chặn, bỏ folder đó khỏi danh sách backup hoặc chỉ chọn những folder dữ liệu thật sự cần backup

App không tự bỏ qua file lỗi vì bỏ qua âm thầm có thể làm backup thiếu dữ liệu.

## Build từ source

Cài thư viện:

```powershell
python -m pip install -r requirements.txt
```

Build file EXE tuỳ chọn cho người phát triển:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name BackupToolPro --collect-data customtkinter src\backup_tool_modern.py
```

## English Quick Guide

1. Download `dist/BackupToolPro-portable.zip`
2. Extract the ZIP file
3. Run `Open_BackupToolPro.bat`
4. The app opens on `Saved configurations`
5. Select an old configuration to load/run it, or click `Create new config`
6. Add files/folders, choose destination, schedule, then run or install schedule

The app verifies copied files with SHA-256 and creates `backup_manifest.json` for every backup.
