# Lộc Phát Design Backup Pro

Portable backup tool for Windows with Vietnamese/English UI, scheduled backups, ZIP output, SHA-256 verification, and backup manifests.

## Download

Use the ready-to-run portable package:

`dist/BackupToolPro-portable.zip`

Extract the ZIP into a writable folder, then run:

`BackupToolPro.exe`

## Features

- Vietnamese / English language switch.
- Backup files and folders.
- Daily, weekly, or custom weekday schedule.
- ZIP archive option.
- Keep only the latest N backups.
- Checks source existence and destination free space before backup.
- Verifies copied files with SHA-256.
- Creates `backup_manifest.json` for every backup.
- Validates ZIP output after creating it.
- Fails clearly if a source is missing or verification fails.

## Source

Main source file:

`src/backup_tool_modern.py`

## Build From Source

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Build EXE:

```powershell
python -m PyInstaller --noconfirm --clean --onefile --windowed --name BackupToolPro --collect-data customtkinter src\backup_tool_modern.py
```

The built EXE will be in `dist/` unless a custom output path is provided.

## Notes

- Windows Task Scheduler is used for automatic backup schedules.
- If schedule installation is blocked, run the app as Administrator and try again.
- `backup_config.json` and `backup_log.txt` are created next to the EXE when the app is used.
