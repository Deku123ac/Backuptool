import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

APP_NAME = "LocPhatDesignBackup"
OWNER_NAME = "Lộc Phát Design"
PRODUCT_NAME = "Lộc Phát Design"

TEXT = {
    "vi": {
        "built_for": "",
        "owner_note": "Backup an toàn cho dữ liệu quan trọng.\nVerify SHA-256 sau khi copy.",
        "source_count_suffix": "nguồn",
        "protected_sources": "nguồn đang được bảo vệ",
        "open_log": "Mở log",
        "remove_schedule": "Gỡ lịch tự động",
        "footer": "Cấu hình và log nằm cùng thư mục với EXE.",
        "main_title": "Backup dữ liệu công ty",
        "main_subtitle": "Chọn dữ liệu, chọn nơi lưu, đặt lịch. Mỗi backup đều được verify trước khi báo thành công.",
        "no_config": "Chưa chọn dữ liệu cần backup",
        "destination": "Nơi lưu backup",
        "destination_hint": "Nên chọn ổ đĩa ngoài, NAS hoặc folder đồng bộ riêng",
        "destination_placeholder": "Chọn folder để lưu backup",
        "choose": "Chọn",
        "open": "Mở",
        "schedule": "Lịch backup",
        "schedule_hint": "Mỗi ngày, mỗi tuần, hoặc chỉ các ngày bạn chọn",
        "next_invalid": "Lần backup kế tiếp: nhập giờ hợp lệ",
        "next_daily": "Lần backup kế tiếp",
        "next_choose_day": "Lần backup kế tiếp: chọn ít nhất 1 ngày",
        "next_unknown": "Lần backup kế tiếp: chưa tính được",
        "sources": "Dữ liệu cần backup",
        "add_file": "Thêm file",
        "add_folder": "Thêm folder",
        "remove_selected": "Xóa mục chọn",
        "clear_all": "Xóa tất cả",
        "empty_sources": "Chưa chọn dữ liệu",
        "empty_hint": "Thêm file hoặc folder cần bảo vệ.",
        "zip": "Nén ZIP",
        "keep": "Giữ",
        "latest": "bản backup gần nhất",
        "check": "Kiểm tra",
        "save": "Lưu",
        "install_schedule": "Cài lịch",
        "run_now": "Backup ngay",
        "schedule_installed": "Lịch: đã cài",
        "schedule_not_installed": "Lịch: chưa cài",
        "ready": "Sẵn sàng",
        "valid_config": "Cấu hình hợp lệ",
        "warning_config": "Cảnh báo cấu hình",
        "backup_running": "Đang backup...",
        "backup_success": "Backup thành công",
        "backup_failed": "Backup thất bại",
        "source_added": "Đã thêm nguồn",
        "source_removed": "Đã xóa nguồn",
        "sources_cleared": "Đã xóa danh sách",
        "saved": "Đã lưu cấu hình",
        "installed": "Đã cài lịch",
        "install_failed": "Cài lịch lỗi",
        "removed": "Đã gỡ lịch",
        "remove_failed": "Chưa gỡ được lịch",
        "lang": "Ngôn ngữ",
        "invalid_destination": "Nơi lưu không hợp lệ",
        "choose_destination_first": "Hãy chọn folder lưu backup hợp lệ trước.",
        "missing_sources": "Thiếu dữ liệu",
        "missing_sources_body": "Hãy thêm ít nhất 1 file hoặc folder cần backup.",
        "invalid_time": "Giờ không hợp lệ",
        "invalid_time_body": "Nhập giờ dạng HH:MM, ví dụ 21:00.",
        "missing_days": "Thiếu ngày backup",
        "missing_days_body": "Hãy chọn ít nhất 1 ngày cho lịch tùy chọn.",
        "can_backup": "Có thể backup.",
        "source_size": "Dung lượng nguồn",
        "destination_free": "Dung lượng trống nơi lưu",
        "verify_mode": "Chế độ verify",
        "backup_success_body": "Backup đã xong và đã verify.",
        "backup_failed_body": "Backup chưa hoàn tất. Mở log để xem chi tiết.",
        "schedule_installed_body": "Windows sẽ tự backup theo lịch bạn chọn.",
        "admin_hint": "Hãy thử mở bằng quyền Administrator.",
        "schedule_removed_body": "Đã gỡ lịch backup tự động.",
        "schedule_missing_body": "Có thể lịch chưa tồn tại.",
    },
    "en": {
        "built_for": "",
        "owner_note": "Safe backup for important company data.\nSHA-256 verification after copy.",
        "source_count_suffix": "sources",
        "protected_sources": "protected backup sources",
        "open_log": "Open Log",
        "remove_schedule": "Remove Schedule",
        "footer": "Config and logs stay next to the EXE.",
        "main_title": "Company data backup",
        "main_subtitle": "Pick data, choose destination, set schedule. Every backup is verified before success.",
        "no_config": "No backup data selected",
        "destination": "Backup destination",
        "destination_hint": "Use an external drive, NAS, or dedicated sync folder",
        "destination_placeholder": "Choose backup folder",
        "choose": "Choose",
        "open": "Open",
        "schedule": "Backup schedule",
        "schedule_hint": "Daily, weekly, or selected weekdays",
        "next_invalid": "Next backup: enter a valid time",
        "next_daily": "Next backup",
        "next_choose_day": "Next backup: choose at least one day",
        "next_unknown": "Next backup: not available",
        "sources": "Backup sources",
        "add_file": "Add file",
        "add_folder": "Add folder",
        "remove_selected": "Remove selected",
        "clear_all": "Clear all",
        "empty_sources": "No sources selected",
        "empty_hint": "Add files or folders to protect.",
        "zip": "ZIP archive",
        "keep": "Keep",
        "latest": "latest backups",
        "check": "Check",
        "save": "Save",
        "install_schedule": "Install schedule",
        "run_now": "Run backup",
        "schedule_installed": "Schedule: installed",
        "schedule_not_installed": "Schedule: not installed",
        "ready": "Ready",
        "valid_config": "Configuration valid",
        "warning_config": "Configuration warning",
        "backup_running": "Backing up...",
        "backup_success": "Backup complete",
        "backup_failed": "Backup failed",
        "source_added": "Source added",
        "source_removed": "Source removed",
        "sources_cleared": "Sources cleared",
        "saved": "Configuration saved",
        "installed": "Schedule installed",
        "install_failed": "Schedule failed",
        "removed": "Schedule removed",
        "remove_failed": "Schedule not removed",
        "lang": "Language",
        "invalid_destination": "Invalid destination",
        "choose_destination_first": "Choose a valid backup folder first.",
        "missing_sources": "Missing sources",
        "missing_sources_body": "Add at least one file or folder to backup.",
        "invalid_time": "Invalid time",
        "invalid_time_body": "Use HH:MM format, for example 21:00.",
        "missing_days": "Missing backup days",
        "missing_days_body": "Choose at least one day for custom schedule.",
        "can_backup": "Backup can run.",
        "source_size": "Source size",
        "destination_free": "Destination free space",
        "verify_mode": "Verify mode",
        "backup_success_body": "Backup is complete and verified.",
        "backup_failed_body": "Backup did not finish. Open the log for details.",
        "schedule_installed_body": "Windows will run backups on your schedule.",
        "admin_hint": "Try running as Administrator.",
        "schedule_removed_body": "Automatic backup schedule was removed.",
        "schedule_missing_body": "The schedule may not exist.",
    },
}


def owner_initials(name: str) -> str:
    parts = [part for part in name.replace("-", " ").replace("_", " ").split() if part]
    if not parts:
        return "BP"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return "".join(part[0].upper() for part in parts[:2])


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


BASE_DIR = app_dir()
CONFIG_PATH = BASE_DIR / "backup_config.json"
LOG_PATH = BASE_DIR / "backup_log.txt"
WEEKDAY_LABELS = {
    "MON": "Thu 2",
    "TUE": "Thu 3",
    "WED": "Thu 4",
    "THU": "Thu 5",
    "FRI": "Thu 6",
    "SAT": "Thu 7",
    "SUN": "Chu nhat",
}
FREQUENCY_LABELS = {
    "vi": {"daily": "Mỗi ngày", "weekly": "Mỗi tuần", "custom": "Tùy chọn ngày"},
    "en": {"daily": "Daily", "weekly": "Weekly", "custom": "Custom days"},
}


@dataclass
class BackupConfig:
    sources: list[str]
    destination: str
    frequency: str = "daily"
    time: str = "21:00"
    weekday: str = "MON"
    weekdays: list[str] | None = None
    zip_backup: bool = True
    keep_latest: int = 10
    language: str = "vi"


def default_config() -> BackupConfig:
    return BackupConfig(sources=[], destination="")


def load_config(path: Path = CONFIG_PATH) -> BackupConfig:
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8-sig"))
            current = asdict(default_config())
            current.update(raw)
            current["sources"] = list(current.get("sources") or [])
            current["weekdays"] = list(current.get("weekdays") or [current.get("weekday") or "MON"])
            current["language"] = current.get("language") if current.get("language") in TEXT else "vi"
            return BackupConfig(**current)
        except Exception:
            pass
    return default_config()


def save_config(config: BackupConfig, path: Path = CONFIG_PATH) -> None:
    path.write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8")


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(f"[{timestamp}] {message}\n")


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_files(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    return sorted([item for item in source.rglob("*") if item.is_file()])


def source_dirs(source: Path) -> list[Path]:
    if source.is_file():
        return []
    return [source, *sorted([item for item in source.rglob("*") if item.is_dir()])]


def source_size(source: Path) -> int:
    return sum(item.stat().st_size for item in source_files(source))


def format_bytes(value: int) -> str:
    size = float(value)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


def config_stats(sources: list[str], destination: str, zip_backup: bool) -> tuple[int, int, int, str | None]:
    paths = [Path(source) for source in sources]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        return 0, 0, 0, f"Thieu nguon: {missing[0]}"
    try:
        files = []
        for path in paths:
            files.extend(source_files(path))
        total_bytes = sum(item.stat().st_size for item in files)
    except Exception as exc:
        return 0, 0, 0, f"Khong doc duoc nguon: {exc}"
    required = total_bytes * (2 if zip_backup else 1) + max(512 * 1024 * 1024, int(total_bytes * 0.1))
    if destination and Path(destination).is_dir():
        free_bytes = shutil.disk_usage(destination).free
    else:
        free_bytes = 0
    return len(files), total_bytes, free_bytes, None if free_bytes >= required or not destination else "Dung luong dich co the khong du"


def verify_file_pair(source: Path, target: Path) -> dict:
    if not target.exists():
        raise RuntimeError(f"Verify failed, target missing: {target}")
    source_stat = source.stat()
    target_stat = target.stat()
    if source_stat.st_size != target_stat.st_size:
        raise RuntimeError(f"Verify failed, size mismatch: {source} -> {target}")
    source_hash = sha256_file(source)
    target_hash = sha256_file(target)
    if source_hash != target_hash:
        raise RuntimeError(f"Verify failed, hash mismatch: {source} -> {target}")
    return {
        "type": "file",
        "source": str(source),
        "path": str(target),
        "size": target_stat.st_size,
        "sha256": target_hash,
        "modified": datetime.fromtimestamp(target_stat.st_mtime).isoformat(timespec="seconds"),
    }


def verify_dir_pair(source: Path, target: Path) -> dict:
    if not target.exists() or not target.is_dir():
        raise RuntimeError(f"Verify failed, directory missing: {source} -> {target}")
    return {
        "type": "directory",
        "source": str(source),
        "path": str(target),
        "size": 0,
        "sha256": None,
        "modified": datetime.fromtimestamp(target.stat().st_mtime).isoformat(timespec="seconds"),
    }


def verify_source_copy(source: Path, target: Path) -> list[dict]:
    entries = []
    if source.is_file():
        entries.append(verify_file_pair(source, target))
        return entries

    for source_dir in source_dirs(source):
        relative = Path("") if source_dir == source else source_dir.relative_to(source)
        target_dir = target / relative
        entries.append(verify_dir_pair(source_dir, target_dir))

    for source_file in source_files(source):
        relative = source_file.relative_to(source)
        target_file = target / relative
        entries.append(verify_file_pair(source_file, target_file))
    return entries


def copy_source(source: Path, target_root: Path) -> tuple[Path, list[dict]]:
    target = unique_path(target_root / source.name)
    if source.is_dir():
        shutil.copytree(source, target, copy_function=shutil.copy2)
        entries = verify_source_copy(source, target)
        log(f"OK folder verified: {source} -> {target} ({len(entries)} files)")
    else:
        shutil.copy2(source, target)
        entries = verify_source_copy(source, target)
        log(f"OK file verified: {source} -> {target}")
    return target, entries


def zip_folder(folder: Path, final_name: str) -> Path:
    zip_path = unique_path(folder.parent / f"{final_name}.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in folder.rglob("*"):
            archive.write(item, Path(final_name) / item.relative_to(folder))
    with zipfile.ZipFile(zip_path, "r") as archive:
        bad_file = archive.testzip()
        if bad_file:
            raise RuntimeError(f"ZIP verify failed: {bad_file}")
        if f"{final_name}/backup_manifest.json" not in archive.namelist():
            raise RuntimeError("ZIP verify failed: backup_manifest.json missing")
    shutil.rmtree(folder)
    log(f"ZIP verified: {zip_path}")
    return zip_path


def cleanup_old_backups(destination: Path, keep_latest: int) -> None:
    backups = sorted(
        [item for item in destination.iterdir() if item.name.startswith("backup_") and not item.name.endswith("_FAILED")],
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for old in backups[keep_latest:]:
        try:
            if old.is_dir():
                shutil.rmtree(old)
            else:
                old.unlink()
            log(f"CLEAN: {old}")
        except Exception as exc:
            log(f"CLEAN ERROR: {old} -> {exc}")


def write_manifest(backup_dir: Path, config: BackupConfig, entries: list[dict], total_bytes: int) -> None:
    file_count = sum(1 for entry in entries if entry.get("type") == "file")
    directory_count = sum(1 for entry in entries if entry.get("type") == "directory")
    manifest = {
        "app": "BackupToolPro",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "destination": config.destination,
        "sources": config.sources,
        "file_count": file_count,
        "directory_count": directory_count,
        "total_bytes": total_bytes,
        "entries": entries,
    }
    (backup_dir / "backup_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"MANIFEST: {file_count} files, {directory_count} directories, {total_bytes} bytes")


def fail_backup(temp_dir: Path, final_name: str) -> None:
    if not temp_dir.exists():
        return
    failed_dir = unique_path(temp_dir.parent / f"{final_name}_FAILED")
    try:
        temp_dir.rename(failed_dir)
        log(f"FAILED COPY KEPT: {failed_dir}")
    except Exception as exc:
        log(f"FAILED COPY RENAME ERROR: {exc}")


def run_backup(config_path: Path = CONFIG_PATH) -> int:
    if not config_path.exists():
        log(f"ERROR: Khong tim thay cau hinh {config_path}")
        return 1
    config = load_config(config_path)
    destination = Path(config.destination)
    sources = [Path(source) for source in config.sources]
    if not destination.is_dir():
        log(f"ERROR: Noi luu khong hop le {destination}")
        return 1
    if not sources:
        log("ERROR: Chua co file/folder can backup")
        return 1

    missing_sources = [str(source) for source in sources if not source.exists()]
    if missing_sources:
        for source in missing_sources:
            log(f"ERROR: Nguon backup khong ton tai: {source}")
        return 1

    try:
        total_bytes = sum(source_size(source) for source in sources)
    except Exception as exc:
        log(f"ERROR: Khong tinh duoc dung luong nguon backup -> {exc}")
        return 1

    free_bytes = shutil.disk_usage(destination).free
    reserve_bytes = max(512 * 1024 * 1024, int(total_bytes * 0.1))
    required_bytes = total_bytes * (2 if config.zip_backup else 1) + reserve_bytes
    if free_bytes < required_bytes:
        log(f"ERROR: Khong du dung luong. Can khoang {required_bytes} bytes, con {free_bytes} bytes")
        return 1

    final_name = datetime.now().strftime("backup_%Y-%m-%d_%H-%M-%S")
    backup_dir = unique_path(destination / f".{final_name}.in_progress")
    backup_dir.mkdir(parents=True, exist_ok=False)
    log(f"START: Backup vao {backup_dir}")

    manifest_entries = []
    try:
        for source in sources:
            target, entries = copy_source(source, backup_dir)
            manifest_entries.extend(entries)
            log(f"VERIFIED: {source} -> {target}")
        if not manifest_entries:
            raise RuntimeError("Khong co file nao duoc backup")
        write_manifest(backup_dir, config, manifest_entries, total_bytes)
        if config.zip_backup:
            zip_folder(backup_dir, final_name)
        else:
            final_dir = unique_path(destination / final_name)
            backup_dir.rename(final_dir)
            log(f"FOLDER verified: {final_dir}")
    except Exception as exc:
        log(f"ERROR: Backup failed -> {exc}")
        fail_backup(backup_dir, final_name)
        return 1

    try:
        cleanup_old_backups(destination, max(1, int(config.keep_latest or 10)))
    except Exception as exc:
        log(f"CLEAN ERROR: {exc}")
        return 1

    log("DONE: Backup verified successfully")
    return 0


def normalize_time(value: str) -> str | None:
    parts = value.strip().split(":")
    if len(parts) != 2:
        return None
    try:
        hour, minute = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return f"{hour:02d}:{minute:02d}"


def scheduled_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" --run "{CONFIG_PATH}"'
    return f'"{sys.executable}" "{Path(__file__).resolve()}" --run "{CONFIG_PATH}"'


def task_is_installed() -> bool:
    result = subprocess.run(["schtasks.exe", "/Query", "/TN", APP_NAME], text=True, capture_output=True)
    return result.returncode == 0


def next_backup_text(frequency: str, time_text: str, weekday: str, weekdays: list[str], language: str = "vi") -> str:
    text = TEXT.get(language, TEXT["vi"])
    clean_time = normalize_time(time_text)
    if not clean_time:
        return text["next_invalid"]
    hour, minute = [int(part) for part in clean_time.split(":")]
    now = datetime.now()
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if frequency == "daily":
        if candidate <= now:
            candidate += timedelta(days=1)
        return f"{text['next_daily']}: {candidate.strftime('%a %Y-%m-%d %H:%M')}"

    selected_days = weekdays if frequency == "custom" else [weekday]
    selected_days = [day for day in selected_days if day in WEEKDAY_LABELS]
    if not selected_days:
        return text["next_choose_day"]

    day_order = list(WEEKDAY_LABELS.keys())
    best = None
    for offset in range(8):
        check = now + timedelta(days=offset)
        if day_order[check.weekday()] not in selected_days:
            continue
        candidate = check.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate > now and (best is None or candidate < best):
            best = candidate
    if best is None:
        return text["next_unknown"]
    return f"{text['next_daily']}: {best.strftime('%a %Y-%m-%d %H:%M')}"


class BackupToolApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(PRODUCT_NAME)
        self.geometry("1060x680")
        self.minsize(980, 620)
        self.configure(fg_color="#0b1220")

        self.config_data = load_config()
        self.language = ctk.StringVar(value=self.config_data.language if self.config_data.language in TEXT else "vi")
        self.frequency = ctk.StringVar(value=self.config_data.frequency)
        self.destination = ctk.StringVar(value=self.config_data.destination)
        self.time = ctk.StringVar(value=self.config_data.time)
        self.weekday = ctk.StringVar(value=self.config_data.weekday)
        selected_weekdays = self.config_data.weekdays or [self.config_data.weekday]
        self.weekday_vars = {day: ctk.BooleanVar(value=day in selected_weekdays) for day in WEEKDAY_LABELS}
        self.zip_backup = ctk.BooleanVar(value=self.config_data.zip_backup)
        self.keep_latest = ctk.IntVar(value=self.config_data.keep_latest)
        self.status = ctk.StringVar(value=self.tr("ready"))
        self.schedule_state = ctk.StringVar(value="")
        self.next_backup = ctk.StringVar(value="")
        self.config_summary = ctk.StringVar(value="Chua co cau hinh backup")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.build_sidebar()
        self.build_content()
        self.refresh_sources()
        self.update_weekday_state()
        self.update_schedule_summary()
        self.update_schedule_status()
        self.frequency.trace_add("write", lambda *_: self.update_schedule_summary())
        self.frequency.trace_add("write", lambda *_: self.update_config_summary())
        self.time.trace_add("write", lambda *_: self.update_schedule_summary())
        self.weekday.trace_add("write", lambda *_: self.update_schedule_summary())
        self.destination.trace_add("write", lambda *_: self.update_config_summary())
        self.zip_backup.trace_add("write", lambda *_: self.update_config_summary())
        self.keep_latest.trace_add("write", lambda *_: self.update_config_summary())
        for var in self.weekday_vars.values():
            var.trace_add("write", lambda *_: self.update_schedule_summary())

    def tr(self, key: str) -> str:
        return TEXT.get(self.language.get(), TEXT["vi"]).get(key, key)

    def change_language(self, value: str) -> None:
        self.language.set("en" if value == "English" else "vi")
        self.config_data.language = self.language.get()
        save_config(self.config_data)
        for child in self.winfo_children():
            child.destroy()
        self.status.set(self.tr("ready"))
        self.build_sidebar()
        self.build_content()
        self.refresh_sources()
        self.update_weekday_state()
        self.update_schedule_summary()
        self.update_schedule_status()

    def build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#111827")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=24, pady=(28, 20))
        logo = ctk.CTkFrame(brand, width=58, height=58, fg_color="#2563eb", corner_radius=18)
        logo.pack(anchor="w", pady=(0, 14))
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text=owner_initials(OWNER_NAME), font=("Segoe UI", 22, "bold"), text_color="white").pack(expand=True)
        ctk.CTkLabel(brand, text=PRODUCT_NAME, font=("Segoe UI", 28, "bold"), text_color="#f8fafc").pack(anchor="w")
        ctk.CTkLabel(brand, text="Backup Pro", font=("Segoe UI", 28, "bold"), text_color="#60a5fa").pack(anchor="w")
        if self.tr("built_for"):
            ctk.CTkLabel(
                brand,
                text=self.tr("built_for"),
                font=("Segoe UI", 12, "bold"),
                text_color="#fbbf24",
            ).pack(anchor="w", pady=(8, 0))
        ctk.CTkLabel(
            brand,
            text=self.tr("owner_note"),
            justify="left",
            font=("Segoe UI", 13),
            text_color="#94a3b8",
        ).pack(anchor="w", pady=(12, 0))

        language_card = ctk.CTkFrame(sidebar, fg_color="#0f172a", corner_radius=18)
        language_card.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(language_card, text=self.tr("lang"), font=("Segoe UI", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=16, pady=(12, 6))
        language_switch = ctk.CTkSegmentedButton(
            language_card,
            values=["Tiếng Việt", "English"],
            command=self.change_language,
            height=34,
        )
        language_switch.pack(fill="x", padx=14, pady=(0, 14))
        language_switch.set("English" if self.language.get() == "en" else "Tiếng Việt")

        stat = ctk.CTkFrame(sidebar, fg_color="#0f172a", corner_radius=18)
        stat.pack(fill="x", padx=20, pady=(6, 16))
        self.source_count_label = ctk.CTkLabel(stat, text=f"0 {self.tr('source_count_suffix')}", font=("Segoe UI", 24, "bold"), text_color="#f8fafc")
        self.source_count_label.pack(anchor="w", padx=18, pady=(16, 0))
        ctk.CTkLabel(stat, text=self.tr("protected_sources"), font=("Segoe UI", 12), text_color="#94a3b8").pack(anchor="w", padx=18, pady=(0, 16))

        self.status_pill = ctk.CTkLabel(
            sidebar,
            textvariable=self.status,
            height=42,
            corner_radius=22,
            fg_color="#1d4ed8",
            text_color="white",
            font=("Segoe UI", 13, "bold"),
        )
        self.status_pill.pack(fill="x", padx=20, pady=(0, 16))

        self.schedule_pill = ctk.CTkLabel(
            sidebar,
            textvariable=self.schedule_state,
            height=38,
            corner_radius=19,
            fg_color="#0f172a",
            text_color="#bfdbfe",
            font=("Segoe UI", 12, "bold"),
        )
        self.schedule_pill.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkButton(
            sidebar,
            text=self.tr("open_log"),
            command=self.open_log,
            height=42,
            fg_color="#1f2937",
            hover_color="#374151",
        ).pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkButton(
            sidebar,
            text=self.tr("remove_schedule"),
            command=self.remove_schedule,
            height=42,
            fg_color="#1f2937",
            hover_color="#374151",
        ).pack(fill="x", padx=20)

        ctk.CTkLabel(
            sidebar,
            text=f"{PRODUCT_NAME}\n{self.tr('footer')}",
            justify="left",
            font=("Segoe UI", 11),
            text_color="#64748b",
        ).pack(side="bottom", anchor="w", padx=24, pady=24)

    def build_content(self) -> None:
        content = ctk.CTkFrame(self, fg_color="#0b1220", corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew", padx=26, pady=24)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(top, text=self.tr("main_title"), font=("Segoe UI", 28, "bold"), text_color="#f8fafc").pack(anchor="w")
        ctk.CTkLabel(
            top,
            text=self.tr("main_subtitle"),
            font=("Segoe UI", 13),
            text_color="#94a3b8",
        ).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(
            top,
            textvariable=self.config_summary,
            font=("Segoe UI", 12, "bold"),
            text_color="#bfdbfe",
            fg_color="#111827",
            corner_radius=14,
            padx=14,
            pady=8,
        ).pack(anchor="w", fill="x", pady=(14, 0))

        cards = ctk.CTkFrame(content, fg_color="transparent")
        cards.grid(row=1, column=0, sticky="ew", pady=(22, 16))
        cards.grid_columnconfigure((0, 1), weight=1)

        self.build_destination_card(cards)
        self.build_schedule_card(cards)
        self.build_source_card(content)
        self.build_action_bar(content)

    def build_destination_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=22)
        card.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(card, text=self.tr("destination"), font=("Segoe UI", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(card, text=self.tr("destination_hint"), font=("Segoe UI", 12), text_color="#94a3b8").pack(anchor="w", padx=18)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=16)
        row.grid_columnconfigure(0, weight=1)
        self.destination_entry = ctk.CTkEntry(row, textvariable=self.destination, height=42, placeholder_text=self.tr("destination_placeholder"))
        self.destination_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkButton(row, text=self.tr("choose"), command=self.choose_destination, height=42, width=82).grid(row=0, column=1, padx=(0, 8))
        ctk.CTkButton(row, text=self.tr("open"), command=self.open_destination, height=42, width=70, fg_color="#334155", hover_color="#475569").grid(row=0, column=2)

    def build_schedule_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=22)
        card.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(card, text=self.tr("schedule"), font=("Segoe UI", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(card, text=self.tr("schedule_hint"), font=("Segoe UI", 12), text_color="#94a3b8").pack(anchor="w", padx=18)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(16, 10))
        row.grid_columnconfigure(0, weight=1)
        self.frequency_switch = ctk.CTkSegmentedButton(
            row,
            values=["daily", "weekly", "custom"],
            variable=self.frequency,
            command=lambda _: self.update_weekday_state(),
            height=38,
        )
        self.frequency_switch.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.time_entry = ctk.CTkEntry(row, textvariable=self.time, width=76, height=38, justify="center")
        self.time_entry.grid(row=0, column=1, padx=(0, 10))
        self.weekday_menu = ctk.CTkOptionMenu(row, values=list(WEEKDAY_LABELS.keys()), variable=self.weekday, width=100, height=38)
        self.weekday_menu.grid(row=0, column=2)

        self.custom_days_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.custom_days_frame.pack(fill="x", padx=18, pady=(0, 10))
        for index, day in enumerate(WEEKDAY_LABELS):
            ctk.CTkCheckBox(
                self.custom_days_frame,
                text=day,
                variable=self.weekday_vars[day],
                width=68,
                command=self.update_schedule_summary,
            ).grid(row=index // 4, column=index % 4, sticky="w", padx=(0, 8), pady=4)

        self.next_backup_label = ctk.CTkLabel(
            card,
            textvariable=self.next_backup,
            font=("Segoe UI", 12, "bold"),
            text_color="#bfdbfe",
            anchor="w",
        )
        self.next_backup_label.pack(fill="x", padx=18, pady=(0, 12))

    def build_source_card(self, parent) -> None:
        card = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=22)
        card.grid(row=2, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=self.tr("sources"), font=("Segoe UI", 17, "bold"), text_color="#f8fafc").grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header, text=self.tr("add_file"), command=self.add_file, width=110, height=38).grid(row=0, column=1, padx=(8, 0))
        ctk.CTkButton(header, text=self.tr("add_folder"), command=self.add_folder, width=120, height=38).grid(row=0, column=2, padx=(8, 0))

        self.source_box = ctk.CTkScrollableFrame(card, fg_color="#0f172a", corner_radius=16)
        self.source_box.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 16))
        ctk.CTkButton(footer, text=self.tr("remove_selected"), command=self.remove_selected, height=36, fg_color="#334155", hover_color="#475569").pack(side="left")
        ctk.CTkButton(footer, text=self.tr("clear_all"), command=self.clear_sources, height=36, fg_color="#334155", hover_color="#475569").pack(side="left", padx=10)
        self.selected_source = ctk.StringVar(value="")

    def build_action_bar(self, parent) -> None:
        bar = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=22)
        bar.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        bar.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=18, pady=16)
        ctk.CTkSwitch(left, text=self.tr("zip"), variable=self.zip_backup).pack(side="left", padx=(0, 18))
        ctk.CTkLabel(left, text=self.tr("keep"), text_color="#94a3b8").pack(side="left")
        ctk.CTkEntry(left, textvariable=self.keep_latest, width=58, height=34, justify="center").pack(side="left", padx=8)
        ctk.CTkLabel(left, text=self.tr("latest"), text_color="#94a3b8").pack(side="left")

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", padx=18, pady=16)
        ctk.CTkButton(right, text=self.tr("check"), command=self.validate_only, width=96, height=44, fg_color="#334155", hover_color="#475569").pack(side="left", padx=(0, 10))
        ctk.CTkButton(right, text=self.tr("save"), command=self.save, width=80, height=44, fg_color="#334155", hover_color="#475569").pack(side="left", padx=(0, 10))
        ctk.CTkButton(right, text=self.tr("install_schedule"), command=self.install_schedule, width=126, height=44, fg_color="#2563eb", hover_color="#1d4ed8").pack(side="left", padx=(0, 10))
        ctk.CTkButton(right, text=self.tr("run_now"), command=self.run_now, width=146, height=44, fg_color="#22c55e", hover_color="#16a34a", text_color="#052e16").pack(side="left")

    def refresh_sources(self) -> None:
        for child in self.source_box.winfo_children():
            child.destroy()

        source_count = len(self.config_data.sources)
        self.source_count_label.configure(text=f"{source_count} {self.tr('source_count_suffix')}")
        self.update_config_summary()

        if not self.config_data.sources:
            empty = ctk.CTkFrame(self.source_box, fg_color="transparent")
            empty.pack(fill="both", expand=True, padx=18, pady=28)
            ctk.CTkLabel(empty, text=self.tr("empty_sources"), font=("Segoe UI", 18, "bold"), text_color="#e2e8f0").pack()
            ctk.CTkLabel(empty, text=self.tr("empty_hint"), font=("Segoe UI", 13), text_color="#64748b").pack(pady=(6, 0))
            return

        for source in self.config_data.sources:
            self.add_source_row(source)

    def add_source_row(self, source: str) -> None:
        exists = Path(source).exists()
        row = ctk.CTkFrame(self.source_box, fg_color="#111827", corner_radius=14)
        row.pack(fill="x", padx=10, pady=6)
        row.grid_columnconfigure(1, weight=1)

        marker_color = "#22c55e" if exists else "#ef4444"
        ctk.CTkLabel(row, text="", width=10, height=10, fg_color=marker_color, corner_radius=5).grid(row=0, column=0, padx=(14, 10), pady=14)
        ctk.CTkLabel(row, text=Path(source).name or source, font=("Segoe UI", 13, "bold"), text_color="#f8fafc", anchor="w").grid(row=0, column=1, sticky="ew", pady=(10, 0))
        ctk.CTkLabel(row, text=source, font=("Segoe UI", 11), text_color="#94a3b8", anchor="w").grid(row=1, column=1, sticky="ew", pady=(0, 10))
        ctk.CTkRadioButton(row, text="", variable=self.selected_source, value=source, width=24).grid(row=0, column=2, rowspan=2, padx=12)

    def add_file(self) -> None:
        for file_path in filedialog.askopenfilenames(title=self.tr("add_file")):
            self.add_source(file_path)

    def add_folder(self) -> None:
        self.add_source(filedialog.askdirectory(title=self.tr("add_folder")))

    def add_source(self, source: str) -> None:
        if source and source not in self.config_data.sources:
            self.config_data.sources.append(source)
            self.refresh_sources()
            self.status.set(self.tr("source_added"))

    def remove_selected(self) -> None:
        selected = self.selected_source.get()
        if selected and selected in self.config_data.sources:
            self.config_data.sources.remove(selected)
            self.selected_source.set("")
            self.refresh_sources()
            self.status.set(self.tr("source_removed"))

    def clear_sources(self) -> None:
        if self.config_data.sources and messagebox.askyesno(self.tr("clear_all"), self.tr("clear_all") + "?"):
            self.config_data.sources = []
            self.selected_source.set("")
            self.refresh_sources()
            self.status.set(self.tr("sources_cleared"))

    def choose_destination(self) -> None:
        folder = filedialog.askdirectory(title=self.tr("destination"))
        if folder:
            self.destination.set(folder)

    def open_destination(self) -> None:
        destination = self.destination.get().strip()
        if destination and Path(destination).is_dir():
            os.startfile(destination)
        else:
            messagebox.showwarning(self.tr("invalid_destination"), self.tr("choose_destination_first"))

    def update_weekday_state(self) -> None:
        frequency = self.frequency.get()
        state = "normal" if frequency == "weekly" else "disabled"
        self.weekday_menu.configure(state=state)
        custom_state = "normal" if frequency == "custom" else "disabled"
        for child in self.custom_days_frame.winfo_children():
            child.configure(state=custom_state)
        self.update_schedule_summary()

    def selected_weekdays(self) -> list[str]:
        return [day for day, var in self.weekday_vars.items() if var.get()]

    def update_schedule_summary(self) -> None:
        selected_days = self.selected_weekdays()
        self.next_backup.set(next_backup_text(self.frequency.get(), self.time.get(), self.weekday.get(), selected_days))

    def update_config_summary(self) -> None:
        if not hasattr(self, "config_summary"):
            return
        if not self.config_data.sources:
            self.config_summary.set(self.tr("no_config"))
            return
        file_count, total_bytes, free_bytes, warning = config_stats(
            self.config_data.sources,
            self.destination.get().strip(),
            bool(self.zip_backup.get()),
        )
        if self.language.get() == "en":
            summary = f"{file_count} files | Data: {format_bytes(total_bytes)}"
        else:
            summary = f"{file_count} file | Dữ liệu: {format_bytes(total_bytes)}"
        if free_bytes:
            summary += f" | {'Free at destination' if self.language.get() == 'en' else 'Còn trống nơi lưu'}: {format_bytes(free_bytes)}"
        summary += f" | {FREQUENCY_LABELS.get(self.language.get(), FREQUENCY_LABELS['vi']).get(self.frequency.get(), self.frequency.get())}"
        if warning:
            summary += f" | {'WARNING' if self.language.get() == 'en' else 'CẢNH BÁO'}: {warning}"
        self.config_summary.set(summary)

    def update_schedule_status(self) -> None:
        if task_is_installed():
            self.schedule_state.set(self.tr("schedule_installed"))
            self.schedule_pill.configure(fg_color="#064e3b", text_color="#bbf7d0")
        else:
            self.schedule_state.set(self.tr("schedule_not_installed"))
            self.schedule_pill.configure(fg_color="#3f1d1d", text_color="#fecaca")

    def current_config(self) -> BackupConfig | None:
        clean_time = normalize_time(self.time.get())
        if not self.config_data.sources:
            messagebox.showwarning(self.tr("missing_sources"), self.tr("missing_sources_body"))
            return None
        destination = self.destination.get().strip()
        if not destination or not Path(destination).is_dir():
            messagebox.showwarning(self.tr("invalid_destination"), self.tr("choose_destination_first"))
            return None
        if not clean_time:
            messagebox.showwarning(self.tr("invalid_time"), self.tr("invalid_time_body"))
            return None
        selected_days = self.selected_weekdays()
        if self.frequency.get() == "custom" and not selected_days:
            messagebox.showwarning(self.tr("missing_days"), self.tr("missing_days_body"))
            return None
        try:
            keep_latest = max(1, int(self.keep_latest.get() or 1))
        except Exception:
            keep_latest = 10
        return BackupConfig(
            sources=list(self.config_data.sources),
            destination=destination,
            frequency=self.frequency.get(),
            time=clean_time,
            weekday=self.weekday.get() or "MON",
            weekdays=selected_days or [self.weekday.get() or "MON"],
            zip_backup=bool(self.zip_backup.get()),
            keep_latest=keep_latest,
            language=self.language.get(),
        )

    def save(self) -> bool:
        config = self.current_config()
        if not config:
            return False
        self.config_data = config
        save_config(config)
        self.time.set(config.time)
        self.keep_latest.set(config.keep_latest)
        self.status.set(self.tr("saved"))
        self.update_schedule_summary()
        self.update_config_summary()
        return True

    def validate_only(self) -> None:
        config = self.current_config()
        if not config:
            return
        file_count, total_bytes, free_bytes, warning = config_stats(config.sources, config.destination, config.zip_backup)
        if warning:
            self.status.set(self.tr("warning_config"))
            messagebox.showwarning(
                self.tr("warning_config"),
                f"{warning}\n\nFiles: {file_count}\n{self.tr('source_size')}: {format_bytes(total_bytes)}\n{self.tr('destination_free')}: {format_bytes(free_bytes)}",
            )
            return
        self.status.set(self.tr("valid_config"))
        messagebox.showinfo(
            self.tr("valid_config"),
            f"{self.tr('can_backup')}\n\nFiles: {file_count}\n{self.tr('source_size')}: {format_bytes(total_bytes)}\n{self.tr('destination_free')}: {format_bytes(free_bytes)}\n{self.tr('verify_mode')}: SHA-256",
        )

    def run_now(self) -> None:
        if not self.save():
            return
        self.status.set(self.tr("backup_running"))
        self.update_idletasks()
        result = run_backup(CONFIG_PATH)
        if result == 0:
            self.status.set(self.tr("backup_success"))
            self.update_config_summary()
            messagebox.showinfo(self.tr("backup_success"), self.tr("backup_success_body"))
        else:
            self.status.set(self.tr("backup_failed"))
            messagebox.showerror(self.tr("backup_failed"), self.tr("backup_failed_body"))

    def install_schedule(self) -> None:
        if not self.save():
            return
        args = ["/Create", "/F", "/TN", APP_NAME, "/TR", scheduled_command(), "/ST", self.config_data.time]
        if self.config_data.frequency == "daily":
            args.extend(["/SC", "DAILY"])
        else:
            days = self.config_data.weekdays if self.config_data.frequency == "custom" else [self.config_data.weekday]
            args.extend(["/SC", "WEEKLY", "/D", ",".join(days or ["MON"])])
        result = subprocess.run(["schtasks.exe", *args], text=True, capture_output=True)
        if result.returncode == 0:
            self.status.set(self.tr("installed"))
            self.update_schedule_status()
            messagebox.showinfo(self.tr("installed"), self.tr("schedule_installed_body"))
        else:
            self.status.set(self.tr("install_failed"))
            messagebox.showerror(self.tr("install_failed"), result.stderr or result.stdout or self.tr("admin_hint"))

    def remove_schedule(self) -> None:
        result = subprocess.run(["schtasks.exe", "/Delete", "/F", "/TN", APP_NAME], text=True, capture_output=True)
        if result.returncode == 0:
            self.status.set(self.tr("removed"))
            self.update_schedule_status()
            messagebox.showinfo(self.tr("removed"), self.tr("schedule_removed_body"))
        else:
            self.status.set(self.tr("remove_failed"))
            messagebox.showwarning(self.tr("remove_failed"), result.stderr or result.stdout or self.tr("schedule_missing_body"))

    def open_log(self) -> None:
        if not LOG_PATH.exists():
            LOG_PATH.write_text("Chua co log backup.\n", encoding="utf-8")
        os.startfile(LOG_PATH)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", nargs="?", const=str(CONFIG_PATH), help="Run backup with config path")
    args = parser.parse_args()
    if args.run:
        return run_backup(Path(args.run))
    BackupToolApp().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
