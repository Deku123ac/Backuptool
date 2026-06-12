# Lộc Phát Design Backup Pro

Tool backup portable cho Windows, có giao diện Tiếng Việt / English, hỗ trợ backup theo lịch, nén ZIP, kiểm tra SHA-256 và tạo manifest cho mỗi bản backup.

## Tải Về

Cách tải nhanh:

1. Mở trang repo: https://github.com/Deku123ac/Backuptool
2. Bấm vào file `dist/BackupToolPro-portable.zip`
3. Bấm nút `Download raw file` hoặc `View raw` để tải file ZIP về máy
4. Giải nén file `BackupToolPro-portable.zip`
5. Mở `BackupToolPro.exe`

Link file trong repo:

`dist/BackupToolPro-portable.zip`

## Cách Sử Dụng

1. Mở `BackupToolPro.exe`
2. Chọn ngôn ngữ `Tiếng Việt` hoặc `English`
3. Bấm `Thêm file` hoặc `Thêm folder` để chọn dữ liệu cần backup
4. Ở mục `Nơi lưu backup`, bấm `Chọn` để chọn thư mục lưu backup
5. Bấm `Kiểm tra` để kiểm tra cấu hình, dung lượng và dữ liệu nguồn
6. Bấm `Backup ngay` để chạy thử backup
7. Nếu muốn tự động backup, chọn lịch rồi bấm `Cài lịch`

## Chế Độ Lịch

- `daily`: backup mỗi ngày
- `weekly`: backup mỗi tuần vào một ngày đã chọn
- `custom`: backup vào nhiều ngày tùy chọn, ví dụ Thứ 2, Thứ 3, Thứ 4

## Dữ Liệu Backup Được Lưu Như Thế Nào

Mỗi lần backup, tool sẽ tạo một bản backup riêng theo thời gian, ví dụ:

`backup_2026-06-12_21-00-00.zip`

Trong mỗi bản backup có:

- File/folder đã chọn
- `backup_manifest.json`
- Thông tin số file, số thư mục, dung lượng, hash SHA-256

## Cơ Chế An Toàn

Tool chỉ báo thành công khi:

- Tất cả file/folder nguồn còn tồn tại
- Copy đầy đủ dữ liệu
- Verify từng file bằng SHA-256 thành công
- File ZIP tạo xong và kiểm tra không lỗi
- Manifest được tạo thành công

Nếu có lỗi:

- Tool báo thất bại
- Không tạo backup giả
- Không xóa các bản backup cũ
- Chi tiết lỗi nằm trong `backup_log.txt`

## Lưu Ý Quan Trọng

- Nên lưu backup vào ổ đĩa khác, ổ cứng ngoài, NAS hoặc thư mục đồng bộ riêng
- Không nên lưu backup cùng ổ với dữ liệu gốc nếu dữ liệu rất quan trọng
- Sau khi cài lịch, nên bấm `Backup ngay` một lần để kiểm tra trước
- Nếu `Cài lịch` bị Windows chặn quyền, hãy bấm chuột phải vào `BackupToolPro.exe` và chọn `Run as administrator`
- `backup_config.json` và `backup_log.txt` sẽ được tạo cùng thư mục với file EXE

## Build Từ Source

Cài thư viện:

```powershell
python -m pip install -r requirements.txt
```

Build file EXE:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name BackupToolPro --collect-data customtkinter src\backup_tool_modern.py
```

## English Quick Guide

1. Download `dist/BackupToolPro-portable.zip`
2. Extract the ZIP file
3. Run `BackupToolPro.exe`
4. Add files or folders to backup
5. Choose a backup destination
6. Click `Check`
7. Click `Run backup` or `Install schedule`

The app verifies copied files with SHA-256 and creates `backup_manifest.json` for every backup.
