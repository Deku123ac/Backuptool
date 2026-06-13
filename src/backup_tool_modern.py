import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
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
        "daily_rule": "Mỗi ngày: backup sẽ chạy mỗi ngày lúc {time}. Không cần tick ngày bên dưới.",
        "weekly_rule": "Mỗi tuần: backup sẽ chạy vào {day} lúc {time}.",
        "custom_rule": "Tùy chọn ngày: backup sẽ chạy vào {days} lúc {time}.",
        "custom_rule_empty": "Tùy chọn ngày: hãy tick ít nhất một ngày để cài lịch.",
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
        "backup_progress": "Tiến trình backup",
        "progress_idle": "Chưa chạy backup",
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
        "hour": "Giờ",
        "minute": "Phút",
        "missing_days": "Thiếu ngày backup",
        "missing_days_body": "Hãy chọn ít nhất 1 ngày cho lịch tùy chọn.",
        "can_backup": "Có thể backup.",
        "source_size": "Dung lượng nguồn",
        "destination_free": "Dung lượng trống nơi lưu",
        "verify_mode": "Chế độ verify",
        "backup_success_body": "Backup đã xong và đã verify.",
        "backup_failed_body": "Backup chưa hoàn tất. Mở log để xem chi tiết.",
        "permission_hint": "Có file/folder Windows không cho đọc. Hãy đóng phần mềm đang dùng file đó, chạy app bằng quyền Administrator, hoặc bỏ file/folder đó khỏi danh sách backup.",
        "schedule_installed_body": "Windows sẽ tự backup theo lịch bạn chọn.",
        "admin_hint": "Hãy thử mở bằng quyền Administrator.",
        "schedule_removed_body": "Đã gỡ lịch backup tự động.",
        "schedule_missing_body": "Có thể lịch chưa tồn tại.",
        "saved_configs": "Cấu hình đã lưu",
        "saved_configs_hint": "Chọn cấu hình cũ để tải lại hoặc chạy ngay.",
        "empty_saved_configs": "Chưa có cấu hình đã lưu",
        "empty_saved_configs_body": "Sau khi bấm Kiểm tra, Cài lịch hoặc Backup ngay, cấu hình hợp lệ sẽ tự lưu ở đây.",
        "create_new_config": "Tạo cấu hình mới",
        "load_config": "Chỉnh sửa cấu hình",
        "run_config": "Chạy cấu hình này",
        "delete_config": "Xóa cấu hình",
        "config_loaded": "Đã tải cấu hình",
        "config_deleted": "Đã xóa cấu hình",
        "choose_saved_config": "Hãy chọn một cấu hình đã lưu trước.",
        "finish": "Hoàn tất",
        "editing_config": "Đang chỉnh sửa",
        "running_config": "Đang chạy",
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
        "daily_rule": "Daily: backup will run every day at {time}. No weekday checkbox is needed.",
        "weekly_rule": "Weekly: backup will run on {day} at {time}.",
        "custom_rule": "Custom days: backup will run on {days} at {time}.",
        "custom_rule_empty": "Custom days: choose at least one weekday before installing schedule.",
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
        "backup_progress": "Backup progress",
        "progress_idle": "No backup running",
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
        "hour": "Hour",
        "minute": "Minute",
        "missing_days": "Missing backup days",
        "missing_days_body": "Choose at least one day for custom schedule.",
        "can_backup": "Backup can run.",
        "source_size": "Source size",
        "destination_free": "Destination free space",
        "verify_mode": "Verify mode",
        "backup_success_body": "Backup is complete and verified.",
        "backup_failed_body": "Backup did not finish. Open the log for details.",
        "permission_hint": "Windows blocked access to a file/folder. Close the app using it, run this tool as Administrator, or remove that file/folder from the backup list.",
        "schedule_installed_body": "Windows will run backups on your schedule.",
        "admin_hint": "Try running as Administrator.",
        "schedule_removed_body": "Automatic backup schedule was removed.",
        "schedule_missing_body": "The schedule may not exist.",
        "saved_configs": "Saved configurations",
        "saved_configs_hint": "Select an old configuration to load or run.",
        "empty_saved_configs": "No saved configurations",
        "empty_saved_configs_body": "After Check, Install schedule, or Run backup, a valid configuration is saved here automatically.",
        "create_new_config": "Create new config",
        "load_config": "Edit config",
        "run_config": "Run this config",
        "delete_config": "Delete config",
        "config_loaded": "Configuration loaded",
        "config_deleted": "Configuration deleted",
        "choose_saved_config": "Choose a saved configuration first.",
        "finish": "Finish",
        "editing_config": "Editing",
        "running_config": "Running",
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
SAVED_CONFIGS_PATH = BASE_DIR / "saved_backup_configs.json"
MAX_SAVED_CONFIGS = 20
SKIPPED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}
WEEKDAY_LABELS = {
    "MON": "Thứ 2",
    "TUE": "Thứ 3",
    "WED": "Thứ 4",
    "THU": "Thứ 5",
    "FRI": "Thứ 6",
    "SAT": "Thứ 7",
    "SUN": "Chủ nhật",
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2), encoding="utf-8")


def config_signature(config: BackupConfig) -> str:
    payload = {
        "sources": list(config.sources),
        "destination": config.destination,
        "frequency": config.frequency,
        "time": config.time,
        "weekday": config.weekday,
        "weekdays": list(config.weekdays or []),
        "zip_backup": bool(config.zip_backup),
        "keep_latest": int(config.keep_latest or 10),
    }
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def config_display_name(config: BackupConfig) -> str:
    if config.sources:
        if len(config.sources) == 1:
            source_name = Path(config.sources[0]).name or config.sources[0]
        else:
            source_name = f"{len(config.sources)} nguồn"
    else:
        source_name = "Chưa có nguồn"
    destination_name = Path(config.destination).name or config.destination or "Chưa chọn nơi lưu"
    return f"{source_name} -> {destination_name}"


def load_saved_configs() -> list[dict]:
    if not SAVED_CONFIGS_PATH.exists():
        return []
    try:
        raw = json.loads(SAVED_CONFIGS_PATH.read_text(encoding="utf-8-sig"))
        items = raw.get("items", raw if isinstance(raw, list) else [])
        return [item for item in items if isinstance(item, dict) and item.get("config")]
    except Exception:
        return []


def save_saved_configs(items: list[dict]) -> None:
    SAVED_CONFIGS_PATH.write_text(
        json.dumps({"items": items[:MAX_SAVED_CONFIGS]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def upsert_saved_config(config: BackupConfig, existing_id: str = "") -> str:
    items = load_saved_configs()
    signature = config_signature(config)
    item_ids = {item.get("id") for item in items}
    config_id = existing_id if existing_id in item_ids else signature
    now = datetime.now().isoformat(timespec="seconds")
    entry = {
        "id": config_id,
        "name": config_display_name(config),
        "updated_at": now,
        "config": asdict(config),
    }
    items = [item for item in items if item.get("id") not in {config_id, signature}]
    items.insert(0, entry)
    save_saved_configs(items)
    return config_id


def delete_saved_config(config_id: str) -> None:
    save_saved_configs([item for item in load_saved_configs() if item.get("id") != config_id])


def log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(f"[{timestamp}] {message}\n")


def last_error_from_log() -> str:
    if not LOG_PATH.exists():
        return ""
    try:
        lines = LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return ""
    for line in reversed(lines[-250:]):
        if "ERROR:" in line or "Backup failed" in line:
            return line
    return ""


def unique_path(path: Path) -> Path:
    if not path_exists(path):
        return path
    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not path_exists(candidate):
            return candidate
        counter += 1


def windows_long_path(path: Path | str) -> str:
    text = str(Path(path).resolve())
    if os.name != "nt" or text.startswith("\\\\?\\"):
        return text
    if text.startswith("\\\\"):
        return "\\\\?\\UNC\\" + text.lstrip("\\")
    return "\\\\?\\" + text


def windows_normal_path(path: str) -> Path:
    if os.name != "nt":
        return Path(path)
    if path.startswith("\\\\?\\UNC\\"):
        return Path("\\\\" + path[8:])
    if path.startswith("\\\\?\\"):
        return Path(path[4:])
    return Path(path)


def path_exists(path: Path) -> bool:
    return os.path.exists(windows_long_path(path))


def path_stat(path: Path):
    return os.stat(windows_long_path(path))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(windows_long_path(path), "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def filtered_walk(source: Path):
    for root, dir_names, file_names in os.walk(windows_long_path(source)):
        root_path = windows_normal_path(root)
        skipped = [name for name in dir_names if name in SKIPPED_DIR_NAMES]
        if skipped:
            log(f"SKIP TECH FOLDERS: {root_path} -> {', '.join(sorted(skipped))}")
        dir_names[:] = sorted(name for name in dir_names if name not in SKIPPED_DIR_NAMES)
        yield root_path, dir_names, sorted(file_names)


def source_files(source: Path) -> list[Path]:
    if os.path.isfile(windows_long_path(source)):
        return [source]
    files = []
    for root, _dir_names, file_names in filtered_walk(source):
        files.extend(root / name for name in file_names)
    return sorted(files)


def source_dirs(source: Path) -> list[Path]:
    if os.path.isfile(windows_long_path(source)):
        return []
    dirs = []
    for root, dir_names, _file_names in filtered_walk(source):
        dirs.append(root)
        dirs.extend(root / name for name in dir_names)
    return sorted(set(dirs))


def source_size(source: Path) -> int:
    return sum(item.stat().st_size for item in source_files(source))


def scan_source_plan(sources: list[Path]) -> tuple[int, int]:
    total_bytes = 0
    total_items = 0
    for source in sources:
        if os.path.isfile(windows_long_path(source)):
            total_bytes += path_stat(source).st_size
            total_items += 1
            continue
        for root, dir_names, file_names in filtered_walk(source):
            total_items += 1 + len(file_names)
            for file_name in file_names:
                total_bytes += path_stat(Path(root) / file_name).st_size
    return total_bytes, max(1, total_items)


def explain_access_error(path: Path, exc: Exception) -> str:
    return (
        f"Không có quyền đọc/ghi: {path}. "
        "Hãy đóng phần mềm đang dùng file này, chạy app bằng quyền Administrator, "
        "hoặc bỏ file/folder này khỏi danh sách backup. "
        f"Chi tiết: {exc}"
    )


def assert_readable_file(path: Path) -> None:
    try:
        with path.open("rb") as fh:
            fh.read(1)
    except PermissionError as exc:
        raise PermissionError(explain_access_error(path, exc)) from exc
    except OSError as exc:
        raise OSError(f"Không đọc được file: {path}. Chi tiết: {exc}") from exc


def preflight_access_check(sources: list[Path], destination: Path) -> None:
    try:
        destination.mkdir(parents=True, exist_ok=True)
        probe = unique_path(destination / ".backup_write_test.tmp")
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except Exception as exc:
        raise RuntimeError(f"Không ghi được vào nơi lưu backup: {destination}. Chi tiết: {exc}") from exc

    for source in sources:
        try:
            path_stat(source)
            if os.path.isfile(windows_long_path(source)):
                assert_readable_file(source)
        except PermissionError:
            raise
        except OSError as exc:
            raise RuntimeError(f"Không đọc được nguồn backup: {source}. Chi tiết: {exc}") from exc


def format_bytes(value: int) -> str:
    size = float(value)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


def config_stats(sources: list[str], destination: str, zip_backup: bool) -> tuple[int, int, int, str | None]:
    paths = [Path(source) for source in sources]
    missing = [str(path) for path in paths if not path_exists(path)]
    if missing:
        return 0, 0, 0, f"Thieu nguon: {missing[0]}"
    if destination and path_exists(Path(destination)) and os.path.isdir(windows_long_path(Path(destination))):
        try:
            preflight_access_check(paths, Path(destination))
        except Exception as exc:
            return 0, 0, 0, str(exc)
    try:
        files = []
        for path in paths:
            files.extend(source_files(path))
        total_bytes = sum(path_stat(item).st_size for item in files)
    except Exception as exc:
        return 0, 0, 0, f"Khong doc duoc nguon: {exc}"
    required = total_bytes * (2 if zip_backup else 1) + max(512 * 1024 * 1024, int(total_bytes * 0.1))
    if destination and path_exists(Path(destination)) and os.path.isdir(windows_long_path(Path(destination))):
        free_bytes = shutil.disk_usage(destination).free
    else:
        free_bytes = 0
    return len(files), total_bytes, free_bytes, None if free_bytes >= required or not destination else "Dung luong dich co the khong du"


def quick_config_stats(sources: list[str], destination: str) -> tuple[int, int, str | None]:
    paths = [Path(source) for source in sources]
    missing = [str(path) for path in paths if not path_exists(path)]
    if missing:
        return 0, 0, f"Thieu nguon: {missing[0]}"
    count = len(paths)
    try:
        free_bytes = shutil.disk_usage(destination).free if destination and path_exists(Path(destination)) and os.path.isdir(windows_long_path(Path(destination))) else 0
    except Exception:
        free_bytes = 0
    return count, free_bytes, None


def verify_file_pair(source: Path, target: Path) -> dict:
    if not path_exists(target):
        raise RuntimeError(f"Verify failed, target missing: {target}")
    source_stat = path_stat(source)
    target_stat = path_stat(target)
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
    if not path_exists(target) or not os.path.isdir(windows_long_path(target)):
        raise RuntimeError(f"Verify failed, directory missing: {source} -> {target}")
    return {
        "type": "directory",
        "source": str(source),
        "path": str(target),
        "size": 0,
        "sha256": None,
        "modified": datetime.fromtimestamp(path_stat(target).st_mtime).isoformat(timespec="seconds"),
    }


def verify_source_copy(source: Path, target: Path, progress_callback=None, progress_state: dict | None = None) -> list[dict]:
    entries = []
    if progress_state is None:
        progress_state = {"done": 0, "total": 1}

    def tick(message: str) -> None:
        progress_state["done"] += 1
        if progress_callback:
            progress_callback(progress_state["done"], progress_state["total"], message)

    if source.is_file():
        entries.append(verify_file_pair(source, target))
        tick(source.name)
        return entries

    for source_dir in source_dirs(source):
        relative = Path("") if source_dir == source else source_dir.relative_to(source)
        target_dir = target / relative
        entries.append(verify_dir_pair(source_dir, target_dir))
        tick(str(relative) if str(relative) else source.name)

    for source_file in source_files(source):
        relative = source_file.relative_to(source)
        target_file = target / relative
        entries.append(verify_file_pair(source_file, target_file))
        tick(str(relative))
    return entries


def copy_source(source: Path, target_root: Path, progress_callback=None, progress_state: dict | None = None) -> tuple[Path, list[dict]]:
    target = unique_path(target_root / source.name)
    entries = []
    if progress_state is None:
        progress_state = {"done": 0, "total": 1}

    def tick(message: str) -> None:
        progress_state["done"] += 1
        if progress_callback:
            progress_callback(progress_state["done"], progress_state["total"], message)

    if os.path.isfile(windows_long_path(source)):
        try:
            shutil.copy2(windows_long_path(source), windows_long_path(target))
            entries.append(verify_file_pair(source, target))
        except PermissionError as exc:
            raise PermissionError(explain_access_error(source, exc)) from exc
        except OSError as exc:
            raise OSError(f"Không copy được file: {source}. Chi tiết: {exc}") from exc
        tick(source.name)
        log(f"OK file verified: {source} -> {target}")
        return target, entries

    os.makedirs(windows_long_path(target), exist_ok=False)
    entries.append(verify_dir_pair(source, target))
    tick(source.name)
    for root_path, dir_names, file_names in filtered_walk(source):
        relative_root = Path("") if root_path == source else root_path.relative_to(source)
        target_root_dir = target / relative_root
        for dir_name in dir_names:
            source_dir = root_path / dir_name
            target_dir = target_root_dir / dir_name
            try:
                os.makedirs(windows_long_path(target_dir), exist_ok=True)
                shutil.copystat(windows_long_path(source_dir), windows_long_path(target_dir), follow_symlinks=False)
                entries.append(verify_dir_pair(source_dir, target_dir))
            except PermissionError as exc:
                raise PermissionError(explain_access_error(source_dir, exc)) from exc
            except OSError as exc:
                raise OSError(f"Không tạo được folder: {target_dir}. Chi tiết: {exc}") from exc
            tick(str(source_dir.relative_to(source)))
        for file_name in file_names:
            source_file = root_path / file_name
            target_file = target_root_dir / file_name
            try:
                shutil.copy2(windows_long_path(source_file), windows_long_path(target_file))
                entries.append(verify_file_pair(source_file, target_file))
            except PermissionError as exc:
                raise PermissionError(explain_access_error(source_file, exc)) from exc
            except OSError as exc:
                raise OSError(f"Không copy được file: {source_file}. Chi tiết: {exc}") from exc
            tick(str(source_file.relative_to(source)))
    log(f"OK folder verified: {source} -> {target} ({len(entries)} items)")
    return target, entries


def zip_folder(folder: Path, final_name: str) -> Path:
    zip_path = unique_path(folder.parent / f"{final_name}.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for root, dir_names, file_names in filtered_walk(folder):
            items = [root / name for name in dir_names] + [root / name for name in file_names]
            for item in items:
                try:
                    archive.write(windows_long_path(item), Path(final_name) / item.relative_to(folder))
                except PermissionError as exc:
                    raise PermissionError(explain_access_error(item, exc)) from exc
                except OSError as exc:
                    raise OSError(f"Không nén được file/folder: {item}. Chi tiết: {exc}") from exc
    with zipfile.ZipFile(zip_path, "r") as archive:
        bad_file = archive.testzip()
        if bad_file:
            raise RuntimeError(f"ZIP verify failed: {bad_file}")
        if f"{final_name}/backup_manifest.json" not in archive.namelist():
            raise RuntimeError("ZIP verify failed: backup_manifest.json missing")
    shutil.rmtree(windows_long_path(folder))
    log(f"ZIP verified: {zip_path}")
    return zip_path


def cleanup_old_backups(destination: Path, keep_latest: int) -> None:
    backups = sorted(
        [item for item in destination.iterdir() if item.name.startswith("backup_") and not item.name.endswith("_FAILED")],
        key=lambda item: path_stat(item).st_mtime,
        reverse=True,
    )
    for old in backups[keep_latest:]:
        try:
            if old.is_dir():
                shutil.rmtree(windows_long_path(old))
            else:
                os.unlink(windows_long_path(old))
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
    with open(windows_long_path(backup_dir / "backup_manifest.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(manifest, ensure_ascii=False, indent=2))
    log(f"MANIFEST: {file_count} files, {directory_count} directories, {total_bytes} bytes")


def fail_backup(temp_dir: Path, final_name: str) -> None:
    if not path_exists(temp_dir):
        return
    failed_dir = unique_path(temp_dir.parent / f"{final_name}_FAILED")
    try:
        os.replace(windows_long_path(temp_dir), windows_long_path(failed_dir))
        log(f"FAILED COPY KEPT: {failed_dir}")
    except Exception as exc:
        log(f"FAILED COPY RENAME ERROR: {exc}")


def run_backup(config_path: Path = CONFIG_PATH, progress_callback=None) -> int:
    if not config_path.exists():
        log(f"ERROR: Khong tim thay cau hinh {config_path}")
        return 1
    config = load_config(config_path)
    destination = Path(config.destination)
    sources = [Path(source) for source in config.sources]
    if not path_exists(destination) or not os.path.isdir(windows_long_path(destination)):
        log(f"ERROR: Noi luu khong hop le {destination}")
        return 1
    if not sources:
        log("ERROR: Chua co file/folder can backup")
        return 1

    missing_sources = [str(source) for source in sources if not path_exists(source)]
    if missing_sources:
        for source in missing_sources:
            log(f"ERROR: Nguon backup khong ton tai: {source}")
        return 1

    if progress_callback:
        progress_callback(0, 1, "Đang đếm file...")
    try:
        total_bytes, total_items = scan_source_plan(sources)
    except Exception as exc:
        log(f"ERROR: Khong tinh duoc dung luong nguon backup -> {exc}")
        return 1

    if progress_callback:
        progress_callback(0, total_items, "Đang kiểm tra nơi lưu...")
    try:
        preflight_access_check(sources, destination)
    except Exception as exc:
        log(f"ERROR: Kiem tra quyen doc/ghi that bai -> {exc}")
        return 1

    free_bytes = shutil.disk_usage(destination).free
    reserve_bytes = max(512 * 1024 * 1024, int(total_bytes * 0.1))
    required_bytes = total_bytes * (2 if config.zip_backup else 1) + reserve_bytes
    if free_bytes < required_bytes:
        log(f"ERROR: Khong du dung luong. Can khoang {required_bytes} bytes, con {free_bytes} bytes")
        return 1

    final_name = datetime.now().strftime("backup_%Y-%m-%d_%H-%M-%S")
    backup_dir = unique_path(destination / f".{final_name}.in_progress")
    os.makedirs(windows_long_path(backup_dir), exist_ok=False)
    log(f"START: Backup vao {backup_dir}")

    manifest_entries = []
    progress_state = {"done": 0, "total": total_items}
    if progress_callback:
        progress_callback(0, total_items, "Bắt đầu copy")
    try:
        for source in sources:
            target, entries = copy_source(source, backup_dir, progress_callback, progress_state)
            manifest_entries.extend(entries)
            log(f"VERIFIED: {source} -> {target}")
        if not manifest_entries:
            raise RuntimeError("Khong co file nao duoc backup")
        write_manifest(backup_dir, config, manifest_entries, total_bytes)
        if config.zip_backup:
            if progress_callback:
                progress_callback(total_items, total_items, "Đang nén ZIP...")
            zip_folder(backup_dir, final_name)
        else:
            if progress_callback:
                progress_callback(total_items, total_items, "Đang hoàn tất...")
            final_dir = unique_path(destination / final_name)
            os.replace(windows_long_path(backup_dir), windows_long_path(final_dir))
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


def split_time(value: str) -> tuple[str, str]:
    clean_time = normalize_time(value) or "21:00"
    hour, minute = clean_time.split(":")
    return hour, minute


def scheduled_command(config_path: Path = CONFIG_PATH) -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" --run "{config_path}"'
    return f'"{sys.executable}" "{Path(__file__).resolve()}" --run "{config_path}"'


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
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = min(1180, max(980, screen_width - 120))
        window_height = min(680, max(600, screen_height - 160))
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(920, 560)
        self.configure(fg_color="#0b1220")

        self.config_data = load_config()
        self.language = ctk.StringVar(value=self.config_data.language if self.config_data.language in TEXT else "vi")
        self.frequency = ctk.StringVar(value=self.config_data.frequency)
        self.frequency_choice = ctk.StringVar(value="")
        self.destination = ctk.StringVar(value=self.config_data.destination)
        self.time = ctk.StringVar(value=self.config_data.time)
        initial_hour, initial_minute = split_time(self.config_data.time)
        self.hour = ctk.StringVar(value=initial_hour)
        self.minute = ctk.StringVar(value=initial_minute)
        self.weekday = ctk.StringVar(value=self.config_data.weekday)
        self.weekday_choice = ctk.StringVar(value=WEEKDAY_LABELS.get(self.config_data.weekday, "Thứ 2"))
        selected_weekdays = self.config_data.weekdays or [self.config_data.weekday]
        self.weekday_vars = {day: ctk.BooleanVar(value=day in selected_weekdays) for day in WEEKDAY_LABELS}
        self.zip_backup = ctk.BooleanVar(value=self.config_data.zip_backup)
        self.keep_latest = ctk.IntVar(value=self.config_data.keep_latest)
        self.status = ctk.StringVar(value=self.tr("ready"))
        self.schedule_state = ctk.StringVar(value="")
        self.next_backup = ctk.StringVar(value="")
        self.schedule_detail = ctk.StringVar(value="")
        self.config_summary = ctk.StringVar(value="Chưa có cấu hình backup")
        self.progress_text = ctk.StringVar(value=self.tr("progress_idle"))
        self.selected_saved_config = ctk.StringVar(value="")
        self.editing_saved_config_id = ""
        self.running_saved_config_id = ""
        self.is_backing_up = False
        self.lockable_controls = []
        self.step_tabs = []
        self.current_step_index = 0
        self.syncing_weekdays = False
        self.frequency_choice.set(self.frequency_label_for(self.frequency.get()))

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
        self.hour.trace_add("write", lambda *_: self.sync_time_from_selectors())
        self.minute.trace_add("write", lambda *_: self.sync_time_from_selectors())
        self.time.trace_add("write", lambda *_: self.update_schedule_summary())
        self.weekday.trace_add("write", lambda *_: self.on_weekday_changed())
        self.destination.trace_add("write", lambda *_: self.update_config_summary())
        self.zip_backup.trace_add("write", lambda *_: self.update_config_summary())
        self.after(2500, self.recover_controls_if_idle)
        self.keep_latest.trace_add("write", lambda *_: self.update_config_summary())
        for var in self.weekday_vars.values():
            var.trace_add("write", lambda *_: self.update_schedule_summary())

    def tr(self, key: str) -> str:
        return TEXT.get(self.language.get(), TEXT["vi"]).get(key, key)

    def frequency_values(self) -> list[str]:
        labels = FREQUENCY_LABELS.get(self.language.get(), FREQUENCY_LABELS["vi"])
        return [labels["daily"], labels["weekly"], labels["custom"]]

    def frequency_label_for(self, value: str) -> str:
        labels = FREQUENCY_LABELS.get(self.language.get(), FREQUENCY_LABELS["vi"])
        return labels.get(value, labels["daily"])

    def frequency_value_from_label(self, label: str) -> str:
        labels = FREQUENCY_LABELS.get(self.language.get(), FREQUENCY_LABELS["vi"])
        for value, display in labels.items():
            if display == label:
                return value
        return label if label in {"daily", "weekly", "custom"} else "daily"

    def set_frequency_choice(self, label: str) -> None:
        self.frequency.set(self.frequency_value_from_label(label))
        self.update_weekday_state()

    def weekday_value_from_label(self, label: str) -> str:
        for value, display in WEEKDAY_LABELS.items():
            if display == label:
                return value
        return label if label in WEEKDAY_LABELS else "MON"

    def set_weekday_choice(self, label: str) -> None:
        self.weekday.set(self.weekday_value_from_label(label))

    def selected_time(self) -> str:
        return f"{self.hour.get()}:{self.minute.get()}"

    def sync_time_from_selectors(self) -> None:
        self.time.set(self.selected_time())
        self.update_schedule_summary()

    def adjust_time(self, part: str, delta: int) -> None:
        if part == "hour":
            value = (int(self.hour.get()) + delta) % 24
            self.hour.set(f"{value:02d}")
        else:
            value = (int(self.minute.get()) + delta) % 60
            value = value - (value % 5)
            self.minute.set(f"{value:02d}")
        self.sync_time_from_selectors()

    def set_time_from_values(self, hour: int, minute: int) -> None:
        minute = max(0, min(59, int(round(minute))))
        self.hour.set(f"{hour % 24:02d}")
        self.minute.set(f"{minute:02d}")
        if hasattr(self, "hour_slider"):
            self.hour_slider.set(int(self.hour.get()))
        if hasattr(self, "minute_slider"):
            self.minute_slider.set(int(self.minute.get()))
        self.sync_time_from_selectors()

    def set_time_preset(self, value: str) -> None:
        hour, minute = value.split(":")
        self.set_time_from_values(int(hour), int(minute))

    def set_hour_from_slider(self, value: float) -> None:
        self.hour.set(f"{int(round(value)):02d}")
        self.sync_time_from_selectors()

    def set_minute_from_slider(self, value: float) -> None:
        minute = max(0, min(59, int(round(value))))
        self.minute.set(f"{minute:02d}")
        self.sync_time_from_selectors()

    def compact_progress_message(self, message: str) -> str:
        message = str(message or "").strip()
        if not message:
            return ""
        leaf = Path(message).name
        if leaf:
            message = leaf
        return message if len(message) <= 46 else f"...{message[-43:]}"

    def on_weekday_changed(self) -> None:
        label = WEEKDAY_LABELS.get(self.weekday.get(), WEEKDAY_LABELS["MON"])
        if self.weekday_choice.get() != label:
            self.weekday_choice.set(label)
        self.sync_weekday_checks()
        self.update_schedule_summary()

    def change_language(self, value: str) -> None:
        self.language.set("en" if value == "English" else "vi")
        self.config_data.language = self.language.get()
        self.frequency_choice.set(self.frequency_label_for(self.frequency.get()))
        save_config(self.config_data)
        for child in self.winfo_children():
            child.destroy()
        self.lockable_controls = []
        self.status.set(self.tr("ready"))
        self.build_sidebar()
        self.build_content()
        self.refresh_sources()
        self.update_weekday_state()
        self.update_schedule_summary()
        self.update_schedule_status()

    def build_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#111827")
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(22, 14))
        logo = ctk.CTkFrame(brand, width=48, height=48, fg_color="#2563eb", corner_radius=16)
        logo.pack(anchor="w", pady=(0, 12))
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text=owner_initials(OWNER_NAME), font=("Segoe UI", 18, "bold"), text_color="white").pack(expand=True)
        ctk.CTkLabel(brand, text=PRODUCT_NAME, font=("Segoe UI", 24, "bold"), text_color="#f8fafc").pack(anchor="w")
        ctk.CTkLabel(brand, text="Backup Pro", font=("Segoe UI", 24, "bold"), text_color="#60a5fa").pack(anchor="w")
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
            font=("Segoe UI", 12),
            text_color="#94a3b8",
        ).pack(anchor="w", pady=(10, 0))

        language_card = ctk.CTkFrame(sidebar, fg_color="#0f172a", corner_radius=18)
        language_card.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkLabel(language_card, text=self.tr("lang"), font=("Segoe UI", 12, "bold"), text_color="#cbd5e1").pack(anchor="w", padx=14, pady=(10, 5))
        language_switch = ctk.CTkSegmentedButton(
            language_card,
            values=["Tiếng Việt", "English"],
            command=self.change_language,
            height=34,
        )
        language_switch.pack(fill="x", padx=12, pady=(0, 12))
        language_switch.set("English" if self.language.get() == "en" else "Tiếng Việt")

        stat = ctk.CTkFrame(sidebar, fg_color="#0f172a", corner_radius=18)
        stat.pack(fill="x", padx=16, pady=(4, 12))
        self.source_count_label = ctk.CTkLabel(stat, text=f"0 {self.tr('source_count_suffix')}", font=("Segoe UI", 22, "bold"), text_color="#f8fafc")
        self.source_count_label.pack(anchor="w", padx=16, pady=(12, 0))
        ctk.CTkLabel(stat, text=self.tr("protected_sources"), font=("Segoe UI", 11), text_color="#94a3b8").pack(anchor="w", padx=16, pady=(0, 12))

        self.status_pill = ctk.CTkLabel(
            sidebar,
            textvariable=self.status,
            height=42,
            corner_radius=22,
            fg_color="#1d4ed8",
            text_color="white",
            font=("Segoe UI", 13, "bold"),
        )
        self.status_pill.pack(fill="x", padx=16, pady=(0, 12))

        self.schedule_pill = ctk.CTkLabel(
            sidebar,
            textvariable=self.schedule_state,
            height=38,
            corner_radius=19,
            fg_color="#0f172a",
            text_color="#bfdbfe",
            font=("Segoe UI", 12, "bold"),
        )
        self.schedule_pill.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkButton(
            sidebar,
            text=self.tr("open_log"),
            command=self.open_log,
            height=42,
            fg_color="#1f2937",
            hover_color="#374151",
        ).pack(fill="x", padx=16, pady=(0, 8))
        self.sidebar_remove_schedule_button = ctk.CTkButton(
            sidebar,
            text=self.tr("remove_schedule"),
            command=self.remove_schedule,
            height=42,
            fg_color="#1f2937",
            hover_color="#374151",
        )
        self.sidebar_remove_schedule_button.pack(fill="x", padx=16)

        ctk.CTkLabel(
            sidebar,
            text=f"{PRODUCT_NAME}\n{self.tr('footer')}",
            justify="left",
            font=("Segoe UI", 11),
            text_color="#64748b",
        ).pack(side="bottom", anchor="w", padx=20, pady=18)

    def build_content(self) -> None:
        content = ctk.CTkScrollableFrame(self, fg_color="#0b1220", corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew", padx=18, pady=16)
        content.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(content, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(top, text=self.tr("main_title"), font=("Segoe UI", 24, "bold"), text_color="#f8fafc").pack(anchor="w")
        ctk.CTkLabel(
            top,
            text=self.tr("main_subtitle"),
            font=("Segoe UI", 12),
            text_color="#94a3b8",
        ).pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(
            top,
            textvariable=self.config_summary,
            font=("Segoe UI", 12, "bold"),
            text_color="#bfdbfe",
            fg_color="#111827",
            corner_radius=14,
            padx=14,
            pady=6,
        ).pack(anchor="w", fill="x", pady=(10, 0))

        self.step_tabs = ["Đã lưu", "Dữ liệu", "Nơi lưu", "Lịch", "Chạy backup"]
        self.step_descriptions = [
            "Tải lại cấu hình cũ",
            "Chọn file/folder",
            "Chọn nơi lưu an toàn",
            "Đặt ngày và giờ",
            "Kiểm tra, cài lịch, chạy",
        ]
        self.step_buttons = []
        self.step_number_labels = []
        self.step_title_labels = []
        self.step_desc_labels = []
        self.build_step_header(content)

        self.step_content = ctk.CTkFrame(content, fg_color="transparent")
        self.step_content.grid(row=2, column=0, sticky="ew", pady=(12, 10))
        self.step_content.grid_columnconfigure(0, weight=1)
        self.step_frames = []
        for index in range(len(self.step_tabs)):
            frame = ctk.CTkFrame(self.step_content, fg_color="#0b1220")
            frame.grid_columnconfigure(0, weight=1)
            self.step_frames.append(frame)

        self.build_saved_configs_card(self.step_frames[0], row=0)
        self.build_source_card(self.step_frames[1], row=0)
        self.build_destination_card(self.step_frames[2], row=0)
        self.build_schedule_card(self.step_frames[3], row=0)
        self.build_action_bar(self.step_frames[4], row=0)

        nav = ctk.CTkFrame(content, fg_color="transparent")
        nav.grid(row=3, column=0, sticky="ew")
        nav.grid_columnconfigure(0, weight=1)
        self.back_step_button = ctk.CTkButton(nav, text="Quay lại", command=self.previous_step, width=120, height=38, fg_color="#334155", hover_color="#475569")
        self.back_step_button.grid(row=0, column=1, padx=(0, 10))
        self.next_step_button = ctk.CTkButton(nav, text="Tiếp theo", command=self.next_step, width=130, height=38)
        self.next_step_button.grid(row=0, column=2)
        self.lockable_controls.extend([self.back_step_button, self.next_step_button])
        self.show_current_step()
        self.update_step_buttons()

    def build_step_header(self, parent) -> None:
        stepper = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=18)
        stepper.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        for index in range(len(self.step_tabs)):
            stepper.grid_columnconfigure(index, weight=1, uniform="step")
            card = ctk.CTkFrame(
                stepper,
                height=62,
                fg_color="#111827",
                corner_radius=14,
            )
            card.grid(row=0, column=index, sticky="ew", padx=(8 if index == 0 else 4, 8 if index == len(self.step_tabs) - 1 else 4), pady=8)
            card.grid_columnconfigure(1, weight=1)
            number = ctk.CTkLabel(card, text=str(index + 1), width=28, height=28, corner_radius=14, fg_color="#334155", text_color="#cbd5e1", font=("Segoe UI", 13, "bold"))
            number.grid(row=0, column=0, rowspan=2, padx=(10, 8), pady=10)
            title = ctk.CTkLabel(card, text=self.step_tabs[index], text_color="#e2e8f0", font=("Segoe UI", 13, "bold"), anchor="w")
            title.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=(9, 0))
            desc = ctk.CTkLabel(card, text=self.step_descriptions[index], text_color="#94a3b8", font=("Segoe UI", 10), anchor="w")
            desc.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(0, 9))
            self.step_buttons.append(card)
            self.step_number_labels.append(number)
            self.step_title_labels.append(title)
            self.step_desc_labels.append(desc)

    def build_destination_card(self, parent, row: int = 0) -> None:
        card = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=22)
        card.grid(row=row, column=0, sticky="ew", padx=6, pady=6)
        ctk.CTkLabel(card, text=self.tr("destination"), font=("Segoe UI", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=18, pady=(14, 4))
        ctk.CTkLabel(card, text=self.tr("destination_hint"), font=("Segoe UI", 12), text_color="#94a3b8").pack(anchor="w", padx=18)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=14)
        row.grid_columnconfigure(0, weight=1)
        self.destination_entry = ctk.CTkEntry(row, textvariable=self.destination, height=42, placeholder_text=self.tr("destination_placeholder"))
        self.destination_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.choose_dest_button = ctk.CTkButton(row, text=self.tr("choose"), command=self.choose_destination, height=42, width=82)
        self.choose_dest_button.grid(row=0, column=1, padx=(0, 8))
        self.open_dest_button = ctk.CTkButton(row, text=self.tr("open"), command=self.open_destination, height=42, width=70, fg_color="#334155", hover_color="#475569")
        self.open_dest_button.grid(row=0, column=2)
        self.lockable_controls.extend([self.destination_entry, self.choose_dest_button, self.open_dest_button])

    def build_schedule_card(self, parent, row: int = 0) -> None:
        card = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=22)
        card.grid(row=row, column=0, sticky="ew", padx=6, pady=6)
        ctk.CTkLabel(card, text=self.tr("schedule"), font=("Segoe UI", 16, "bold"), text_color="#f8fafc").pack(anchor="w", padx=18, pady=(14, 4))
        ctk.CTkLabel(card, text=self.tr("schedule_hint"), font=("Segoe UI", 12), text_color="#94a3b8").pack(anchor="w", padx=18)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=18, pady=(14, 8))
        row.grid_columnconfigure(0, weight=1)
        self.frequency_switch = ctk.CTkSegmentedButton(
            row,
            values=self.frequency_values(),
            variable=self.frequency_choice,
            command=self.set_frequency_choice,
            height=38,
        )
        self.frequency_switch.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        time_picker = ctk.CTkFrame(row, fg_color="transparent")
        time_picker.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(14, 0))
        time_picker.grid_columnconfigure(1, weight=1)
        time_picker.grid_columnconfigure(3, weight=1)
        preset_row = ctk.CTkFrame(time_picker, fg_color="transparent")
        preset_row.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))
        for preset in ["08:00", "12:00", "18:00", "21:00"]:
            button = ctk.CTkButton(preset_row, text=preset, width=72, height=32, fg_color="#1f2937", hover_color="#2563eb", command=lambda value=preset: self.set_time_preset(value))
            button.pack(side="left", padx=(0, 8))
            self.lockable_controls.append(button)
        ctk.CTkLabel(time_picker, textvariable=self.hour, width=52, height=34, fg_color="#1f2937", corner_radius=10, font=("Segoe UI", 15, "bold")).grid(row=1, column=0, padx=(0, 10))
        self.hour_slider = ctk.CTkSlider(time_picker, from_=0, to=23, number_of_steps=23, command=self.set_hour_from_slider)
        self.hour_slider.grid(row=1, column=1, sticky="ew", padx=(0, 18))
        self.hour_slider.set(int(self.hour.get()))
        ctk.CTkLabel(time_picker, textvariable=self.minute, width=52, height=34, fg_color="#1f2937", corner_radius=10, font=("Segoe UI", 15, "bold")).grid(row=1, column=2, padx=(0, 10))
        self.minute_slider = ctk.CTkSlider(time_picker, from_=0, to=59, number_of_steps=59, command=self.set_minute_from_slider)
        self.minute_slider.grid(row=1, column=3, sticky="ew")
        self.minute_slider.set(int(self.minute.get()))
        self.lockable_controls.extend([self.frequency_switch, self.hour_slider, self.minute_slider])
        self.weekday_menu = ctk.CTkOptionMenu(row, values=list(WEEKDAY_LABELS.values()), variable=self.weekday_choice, command=self.set_weekday_choice, width=120, height=38)
        self.weekday_menu.grid(row=0, column=2)
        self.lockable_controls.append(self.weekday_menu)

        self.custom_days_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.custom_days_frame.pack(fill="x", padx=18, pady=(0, 10))
        for index, day in enumerate(WEEKDAY_LABELS):
            checkbox = ctk.CTkCheckBox(
                self.custom_days_frame,
                text=WEEKDAY_LABELS[day],
                variable=self.weekday_vars[day],
                width=88,
                command=self.update_schedule_summary,
            )
            checkbox.grid(row=index // 4, column=index % 4, sticky="w", padx=(0, 8), pady=4)
            self.lockable_controls.append(checkbox)

        self.next_backup_label = ctk.CTkLabel(
            card,
            textvariable=self.next_backup,
            font=("Segoe UI", 12, "bold"),
            text_color="#bfdbfe",
            anchor="w",
        )
        self.next_backup_label.pack(fill="x", padx=18, pady=(0, 4))
        self.schedule_detail_label = ctk.CTkLabel(
            card,
            textvariable=self.schedule_detail,
            font=("Segoe UI", 12),
            text_color="#93c5fd",
            anchor="w",
            wraplength=980,
        )
        self.schedule_detail_label.pack(fill="x", padx=18, pady=(0, 12))

    def active_step_index(self) -> int:
        return self.current_step_index

    def update_step_buttons(self) -> None:
        if not hasattr(self, "back_step_button") or not hasattr(self, "next_step_button"):
            return
        index = self.active_step_index()
        self.back_step_button.configure(state="normal" if index > 0 else "disabled")
        if index == 0:
            next_text = self.tr("create_new_config")
        elif index == len(self.step_tabs) - 1:
            next_text = self.tr("finish")
        else:
            next_text = "Tiếp theo"
        self.next_step_button.configure(
            text=next_text,
            state="disabled" if self.is_backing_up else "normal",
        )
        if hasattr(self, "step_buttons"):
            for step_index, button in enumerate(self.step_buttons):
                active = step_index == index
                complete = step_index < index
                button.configure(
                    fg_color="#1d4ed8" if active else "#102033" if complete else "#111827",
                )
                self.step_number_labels[step_index].configure(
                    fg_color="#f8fafc" if active else "#22c55e" if complete else "#334155",
                    text_color="#1d4ed8" if active else "#052e16" if complete else "#cbd5e1",
                    text="✓" if complete else str(step_index + 1),
                )
                self.step_title_labels[step_index].configure(text_color="#ffffff" if active else "#dbeafe" if complete else "#e2e8f0")
                self.step_desc_labels[step_index].configure(text_color="#dbeafe" if active else "#93c5fd" if complete else "#94a3b8")

    def show_current_step(self) -> None:
        if hasattr(self, "step_frames") and self.step_frames:
            for index, frame in enumerate(self.step_frames):
                if index == self.current_step_index:
                    frame.grid(row=0, column=0, sticky="ew")
                    frame.tkraise()
                else:
                    frame.grid_remove()
        self.update_step_buttons()

    def go_step(self, index: int) -> None:
        if not self.step_tabs:
            return
        self.current_step_index = max(0, min(index, len(self.step_tabs) - 1))
        self.show_current_step()

    def current_step_ready(self) -> bool:
        index = self.active_step_index()
        if index == 1 and not self.config_data.sources:
            messagebox.showwarning(self.tr("missing_sources"), self.tr("missing_sources_body"))
            return False
        if index == 2:
            destination = self.destination.get().strip()
            if not destination or not Path(destination).is_dir():
                messagebox.showwarning(self.tr("invalid_destination"), self.tr("choose_destination_first"))
                return False
        if index == 3:
            if not normalize_time(self.selected_time()):
                messagebox.showwarning(self.tr("invalid_time"), self.tr("invalid_time_body"))
                return False
            if self.frequency.get() == "custom" and not self.selected_weekdays():
                messagebox.showwarning(self.tr("missing_days"), self.tr("missing_days_body"))
                return False
        return True

    def next_step(self) -> None:
        index = self.active_step_index()
        if index == 0:
            self.start_new_config()
            return
        if index >= len(self.step_tabs) - 1:
            self.finish_configuration()
            return
        if self.current_step_ready():
            self.go_step(index + 1)

    def previous_step(self) -> None:
        self.go_step(self.active_step_index() - 1)

    def start_new_config(self) -> None:
        config = default_config()
        config.language = self.language.get()
        self.editing_saved_config_id = ""
        self.selected_saved_config.set("")
        self.apply_config_to_ui(config)
        self.status.set(self.tr("ready"))
        self.go_step(1)

    def finish_configuration(self) -> None:
        if not self.current_step_ready():
            return
        if not self.save():
            return
        self.refresh_saved_configs()
        self.status.set(self.tr("saved"))
        self.go_step(0)

    def build_source_card(self, parent, row: int = 0) -> None:
        card = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=22)
        card.grid(row=row, column=0, sticky="ew", padx=6, pady=6)
        card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=self.tr("sources"), font=("Segoe UI", 17, "bold"), text_color="#f8fafc").grid(row=0, column=0, sticky="w")
        self.add_file_button = ctk.CTkButton(header, text=self.tr("add_file"), command=self.add_file, width=110, height=38)
        self.add_file_button.grid(row=0, column=1, padx=(8, 0))
        self.add_folder_button = ctk.CTkButton(header, text=self.tr("add_folder"), command=self.add_folder, width=120, height=38)
        self.add_folder_button.grid(row=0, column=2, padx=(8, 0))
        self.lockable_controls.extend([self.add_file_button, self.add_folder_button])

        self.source_box = ctk.CTkScrollableFrame(card, fg_color="#0f172a", corner_radius=16, height=185)
        self.source_box.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 14))
        self.remove_source_button = ctk.CTkButton(footer, text=self.tr("remove_selected"), command=self.remove_selected, height=36, fg_color="#334155", hover_color="#475569")
        self.remove_source_button.pack(side="left")
        self.clear_sources_button = ctk.CTkButton(footer, text=self.tr("clear_all"), command=self.clear_sources, height=36, fg_color="#334155", hover_color="#475569")
        self.clear_sources_button.pack(side="left", padx=10)
        self.lockable_controls.extend([self.remove_source_button, self.clear_sources_button])
        self.selected_source = ctk.StringVar(value="")

    def build_action_bar(self, parent, row: int = 0) -> None:
        bar = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=22)
        bar.grid(row=row, column=0, sticky="ew", padx=6, pady=6)
        bar.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(bar, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=18, pady=(16, 10))
        self.zip_switch = ctk.CTkSwitch(left, text=self.tr("zip"), variable=self.zip_backup)
        self.zip_switch.pack(side="left", padx=(0, 18))
        ctk.CTkLabel(left, text=self.tr("keep"), text_color="#94a3b8").pack(side="left")
        self.keep_entry = ctk.CTkEntry(left, textvariable=self.keep_latest, width=58, height=34, justify="center")
        self.keep_entry.pack(side="left", padx=8)
        ctk.CTkLabel(left, text=self.tr("latest"), text_color="#94a3b8").pack(side="left")
        self.lockable_controls.extend([self.zip_switch, self.keep_entry])

        progress_area = ctk.CTkFrame(bar, fg_color="transparent")
        progress_area.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
        progress_area.grid_columnconfigure(0, weight=1)
        self.progress_bar = ctk.CTkProgressBar(progress_area, height=12, mode="determinate")
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.progress_bar.set(0)
        ctk.CTkLabel(progress_area, textvariable=self.progress_text, width=180, anchor="e", text_color="#bfdbfe", font=("Segoe UI", 12, "bold")).grid(row=0, column=1, sticky="e")

        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.grid(row=2, column=0, sticky="e", padx=18, pady=(4, 16))
        self.check_button = ctk.CTkButton(right, text=self.tr("check"), command=self.validate_only, width=96, height=44, fg_color="#334155", hover_color="#475569")
        self.check_button.pack(side="left", padx=(0, 10))
        self.schedule_button = ctk.CTkButton(right, text=self.tr("install_schedule"), command=self.install_schedule, width=126, height=44, fg_color="#2563eb", hover_color="#1d4ed8")
        self.schedule_button.pack(side="left", padx=(0, 10))
        self.backup_button = ctk.CTkButton(right, text=self.tr("run_now"), command=self.run_now, width=146, height=44, fg_color="#22c55e", hover_color="#16a34a", text_color="#052e16")
        self.backup_button.pack(side="left")
        self.lockable_controls.extend([self.check_button, self.schedule_button, self.backup_button])

    def build_saved_configs_card(self, parent, row: int = 0) -> None:
        card = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=22)
        card.grid(row=row, column=0, sticky="ew", padx=6, pady=6)
        card.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 8))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=self.tr("saved_configs"), font=("Segoe UI", 17, "bold"), text_color="#f8fafc").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text=self.tr("saved_configs_hint"), font=("Segoe UI", 12), text_color="#94a3b8").grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.saved_configs_box = ctk.CTkScrollableFrame(card, fg_color="#0f172a", corner_radius=16, height=250)
        self.saved_configs_box.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 12))

        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="e", padx=18, pady=(0, 14))
        self.load_saved_button = ctk.CTkButton(actions, text=self.tr("load_config"), command=self.load_selected_saved_config, width=152, height=38, fg_color="#334155", hover_color="#475569")
        self.load_saved_button.pack(side="left", padx=(0, 10))
        self.run_saved_button = ctk.CTkButton(actions, text=self.tr("run_config"), command=self.run_selected_saved_config, width=152, height=38, fg_color="#22c55e", hover_color="#16a34a", text_color="#052e16")
        self.run_saved_button.pack(side="left", padx=(0, 10))
        self.delete_saved_button = ctk.CTkButton(actions, text=self.tr("delete_config"), command=self.delete_selected_saved_config, width=118, height=38, fg_color="#7f1d1d", hover_color="#991b1b")
        self.delete_saved_button.pack(side="left")
        self.lockable_controls.extend([self.load_saved_button, self.run_saved_button, self.delete_saved_button])
        self.refresh_saved_configs()

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

    def refresh_saved_configs(self) -> None:
        if not hasattr(self, "saved_configs_box"):
            return
        for child in self.saved_configs_box.winfo_children():
            child.destroy()

        items = load_saved_configs()
        valid_ids = {item.get("id") for item in items}
        if self.selected_saved_config.get() not in valid_ids:
            self.selected_saved_config.set("")

        if not items:
            empty = ctk.CTkFrame(self.saved_configs_box, fg_color="transparent")
            empty.pack(fill="both", expand=True, padx=18, pady=28)
            ctk.CTkLabel(empty, text=self.tr("empty_saved_configs"), font=("Segoe UI", 18, "bold"), text_color="#e2e8f0").pack()
            ctk.CTkLabel(empty, text=self.tr("empty_saved_configs_body"), font=("Segoe UI", 13), text_color="#64748b", wraplength=720).pack(pady=(6, 0))
            ctk.CTkButton(empty, text=self.tr("create_new_config"), command=self.start_new_config, width=180, height=40).pack(pady=(18, 0))
            return

        for item in items:
            self.add_saved_config_row(item)

    def add_saved_config_row(self, item: dict) -> None:
        raw_config = item.get("config") or {}
        config = BackupConfig(**{**asdict(default_config()), **raw_config})
        row = ctk.CTkFrame(self.saved_configs_box, fg_color="#111827", corner_radius=14)
        row.pack(fill="x", padx=10, pady=6)
        row.grid_columnconfigure(0, weight=1)
        title = item.get("name") or config_display_name(config)
        config_id = item.get("id", "")
        badges = []
        if config_id and config_id == self.running_saved_config_id:
            badges.append(self.tr("running_config"))
        if config_id and config_id == self.editing_saved_config_id:
            badges.append(self.tr("editing_config"))
        if config_id and config_id == self.selected_saved_config.get() and not badges:
            badges.append("Đã chọn" if self.language.get() == "vi" else "Selected")
        if badges:
            title = f"{title}  ·  {' / '.join(badges)}"
        frequency_label = FREQUENCY_LABELS.get(self.language.get(), FREQUENCY_LABELS["vi"]).get(config.frequency, config.frequency)
        if config.frequency == "custom":
            days = ", ".join(WEEKDAY_LABELS.get(day, day) for day in (config.weekdays or []))
        elif config.frequency == "weekly":
            days = WEEKDAY_LABELS.get(config.weekday, config.weekday)
        else:
            days = "Mỗi ngày" if self.language.get() == "vi" else "Daily"
        detail = f"{frequency_label} | {config.time} | {days} | {len(config.sources)} nguồn"
        title_label = ctk.CTkLabel(row, text=title, font=("Segoe UI", 13, "bold"), text_color="#f8fafc", anchor="w")
        title_label.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 0))
        detail_label = ctk.CTkLabel(row, text=detail, font=("Segoe UI", 11), text_color="#bfdbfe", anchor="w")
        detail_label.grid(row=1, column=0, sticky="ew", padx=14, pady=(2, 0))
        dest_label = ctk.CTkLabel(row, text=f"Nơi lưu: {config.destination}", font=("Segoe UI", 11), text_color="#94a3b8", anchor="w")
        dest_label.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))
        radio = ctk.CTkRadioButton(row, text="", variable=self.selected_saved_config, value=config_id, width=24, command=lambda value=config_id: self.select_saved_config(value))
        radio.grid(row=0, column=1, rowspan=3, padx=12)
        for widget in (row, title_label, detail_label, dest_label):
            widget.bind("<Button-1>", lambda _event, value=config_id: self.select_saved_config(value))
            widget.bind("<Double-Button-1>", lambda _event, value=config_id: (self.selected_saved_config.set(value), self.load_selected_saved_config()))

    def select_saved_config(self, config_id: str) -> None:
        self.selected_saved_config.set(config_id)
        self.refresh_saved_configs()

    def selected_saved_item(self) -> dict | None:
        selected_id = self.selected_saved_config.get()
        if not selected_id:
            messagebox.showwarning(self.tr("saved_configs"), self.tr("choose_saved_config"))
            return None
        for item in load_saved_configs():
            if item.get("id") == selected_id:
                return item
        messagebox.showwarning(self.tr("saved_configs"), self.tr("choose_saved_config"))
        return None

    def apply_config_to_ui(self, config: BackupConfig) -> None:
        self.config_data = config
        self.destination.set(config.destination)
        self.frequency.set(config.frequency)
        self.frequency_choice.set(self.frequency_label_for(config.frequency))
        hour, minute = split_time(config.time)
        self.hour.set(hour)
        self.minute.set(minute)
        self.time.set(config.time)
        self.weekday.set(config.weekday or "MON")
        self.weekday_choice.set(WEEKDAY_LABELS.get(config.weekday or "MON", WEEKDAY_LABELS["MON"]))
        if config.frequency == "daily":
            selected_weekdays = []
        elif config.frequency == "custom":
            selected_weekdays = config.weekdays or []
        else:
            selected_weekdays = [config.weekday or "MON"]
        for day, var in self.weekday_vars.items():
            var.set(day in selected_weekdays)
        self.zip_backup.set(bool(config.zip_backup))
        self.keep_latest.set(max(1, int(config.keep_latest or 10)))
        if hasattr(self, "hour_slider"):
            self.hour_slider.set(int(hour))
        if hasattr(self, "minute_slider"):
            self.minute_slider.set(int(minute))
        self.refresh_sources()
        self.update_weekday_state()
        self.update_config_summary()

    def load_selected_saved_config(self) -> None:
        item = self.selected_saved_item()
        if not item:
            return
        config = BackupConfig(**{**asdict(default_config()), **(item.get("config") or {})})
        config.language = self.language.get()
        self.apply_config_to_ui(config)
        self.editing_saved_config_id = item.get("id", "")
        self.selected_saved_config.set(self.editing_saved_config_id)
        save_config(config)
        self.status.set(self.tr("config_loaded"))
        self.refresh_saved_configs()
        self.go_step(1)

    def run_selected_saved_config(self) -> None:
        item = self.selected_saved_item()
        if not item:
            return
        config = BackupConfig(**{**asdict(default_config()), **(item.get("config") or {})})
        config.language = self.language.get()
        self.apply_config_to_ui(config)
        self.editing_saved_config_id = item.get("id", "")
        self.selected_saved_config.set(self.editing_saved_config_id)
        save_config(config)
        self.go_step(4)
        self.run_now()

    def delete_selected_saved_config(self) -> None:
        item = self.selected_saved_item()
        if not item:
            return
        if not messagebox.askyesno(self.tr("delete_config"), self.tr("delete_config") + "?"):
            return
        delete_saved_config(item.get("id", ""))
        if self.editing_saved_config_id == item.get("id", ""):
            self.editing_saved_config_id = ""
        if self.running_saved_config_id == item.get("id", ""):
            self.running_saved_config_id = ""
        self.selected_saved_config.set("")
        self.refresh_saved_configs()
        self.status.set(self.tr("config_deleted"))

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
        if self.frequency_choice.get() != self.frequency_label_for(frequency):
            self.frequency_choice.set(self.frequency_label_for(frequency))
        label = WEEKDAY_LABELS.get(self.weekday.get(), WEEKDAY_LABELS["MON"])
        if self.weekday_choice.get() != label:
            self.weekday_choice.set(label)
        if frequency == "daily":
            self.syncing_weekdays = True
            try:
                for var in self.weekday_vars.values():
                    var.set(False)
            finally:
                self.syncing_weekdays = False
        else:
            self.sync_weekday_checks()
        state = "normal" if frequency == "weekly" else "disabled"
        self.weekday_menu.configure(state=state)
        custom_state = "normal" if frequency == "custom" else "disabled"
        for child in self.custom_days_frame.winfo_children():
            child.configure(state=custom_state)
        self.update_schedule_summary()

    def sync_weekday_checks(self) -> None:
        if self.syncing_weekdays:
            return
        frequency = self.frequency.get()
        if frequency == "custom":
            return
        self.syncing_weekdays = True
        try:
            checked_day = self.weekday.get() if frequency == "weekly" else ""
            for day, var in self.weekday_vars.items():
                var.set(day == checked_day)
        finally:
            self.syncing_weekdays = False

    def selected_weekdays(self) -> list[str]:
        if self.frequency.get() == "weekly":
            return [self.weekday.get() or "MON"]
        if self.frequency.get() == "daily":
            return []
        return [day for day, var in self.weekday_vars.items() if var.get()]

    def update_schedule_summary(self) -> None:
        selected_days = self.selected_weekdays()
        self.next_backup.set(next_backup_text(self.frequency.get(), self.selected_time(), self.weekday.get(), selected_days, self.language.get()))
        time_text = normalize_time(self.selected_time()) or self.selected_time()
        frequency = self.frequency.get()
        if frequency == "daily":
            self.schedule_detail.set(self.tr("daily_rule").format(time=time_text))
        elif frequency == "weekly":
            day = WEEKDAY_LABELS.get(self.weekday.get(), self.weekday.get())
            self.schedule_detail.set(self.tr("weekly_rule").format(day=day, time=time_text))
        else:
            if selected_days:
                days = ", ".join(WEEKDAY_LABELS.get(day, day) for day in selected_days)
                self.schedule_detail.set(self.tr("custom_rule").format(days=days, time=time_text))
            else:
                self.schedule_detail.set(self.tr("custom_rule_empty"))

    def update_config_summary(self) -> None:
        if not hasattr(self, "config_summary"):
            return
        if not self.config_data.sources:
            self.config_summary.set(self.tr("no_config"))
            return
        source_count, free_bytes, warning = quick_config_stats(self.config_data.sources, self.destination.get().strip())
        if self.language.get() == "en":
            summary = f"{source_count} sources"
        else:
            summary = f"{source_count} nguồn"
        if free_bytes:
            summary += f" | {'Free at destination' if self.language.get() == 'en' else 'Còn trống nơi lưu'}: {format_bytes(free_bytes)}"
        summary += f" | {FREQUENCY_LABELS.get(self.language.get(), FREQUENCY_LABELS['vi']).get(self.frequency.get(), self.frequency.get())}"
        if warning:
            summary += f" | {'WARNING' if self.language.get() == 'en' else 'CẢNH BÁO'}: {warning}"
        self.config_summary.set(summary)

    def update_schedule_status(self) -> None:
        installed = task_is_installed()
        if installed:
            self.schedule_state.set(self.tr("schedule_installed"))
            self.schedule_pill.configure(fg_color="#064e3b", text_color="#bbf7d0")
        else:
            self.schedule_state.set(self.tr("schedule_not_installed"))
            self.schedule_pill.configure(fg_color="#3f1d1d", text_color="#fecaca")
        if hasattr(self, "sidebar_remove_schedule_button"):
            self.sidebar_remove_schedule_button.configure(state="normal" if installed else "disabled")

    def current_config(self) -> BackupConfig | None:
        clean_time = normalize_time(self.selected_time())
        if not self.config_data.sources:
            messagebox.showwarning(self.tr("missing_sources"), self.tr("missing_sources_body"))
            return None
        destination = self.destination.get().strip()
        destination_path = Path(destination) if destination else None
        if not destination_path or not path_exists(destination_path) or not os.path.isdir(windows_long_path(destination_path)):
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
        stored_weekdays = selected_days if self.frequency.get() != "daily" else []
        return BackupConfig(
            sources=list(self.config_data.sources),
            destination=destination,
            frequency=self.frequency.get(),
            time=clean_time,
            weekday=self.weekday.get() or "MON",
            weekdays=stored_weekdays,
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
        saved_id = upsert_saved_config(config, self.editing_saved_config_id)
        self.editing_saved_config_id = saved_id
        self.selected_saved_config.set(saved_id)
        self.refresh_saved_configs()
        self.time.set(config.time)
        hour, minute = split_time(config.time)
        self.hour.set(hour)
        self.minute.set(minute)
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
        files_label = "Files" if self.language.get() == "en" else "Số file"
        if warning:
            self.status.set(self.tr("warning_config"))
            messagebox.showwarning(
                self.tr("warning_config"),
                f"{warning}\n\n{files_label}: {file_count}\n{self.tr('source_size')}: {format_bytes(total_bytes)}\n{self.tr('destination_free')}: {format_bytes(free_bytes)}",
            )
            return
        self.status.set(self.tr("valid_config"))
        messagebox.showinfo(
            self.tr("valid_config"),
            f"{self.tr('can_backup')}\n\n{files_label}: {file_count}\n{self.tr('source_size')}: {format_bytes(total_bytes)}\n{self.tr('destination_free')}: {format_bytes(free_bytes)}\n{self.tr('verify_mode')}: SHA-256",
        )

    def set_controls_state(self, state: str) -> None:
        for control in self.lockable_controls:
            try:
                control.configure(state=state)
            except Exception:
                pass

    def recover_controls_if_idle(self) -> None:
        if not self.is_backing_up:
            self.set_controls_state("normal")
            self.update_step_buttons()
        self.after(2500, self.recover_controls_if_idle)

    def update_progress(self, done: int, total: int, message: str = "") -> None:
        total = max(1, total)
        percent = min(100, int((done / total) * 100))

        def apply_update() -> None:
            if hasattr(self, "progress_bar"):
                self.progress_bar.set(percent / 100)
            short_message = self.compact_progress_message(message)
            self.progress_text.set(f"{percent}% - {short_message}" if short_message else f"{percent}%")

        self.after(0, apply_update)

    def finish_backup(self, result: int) -> None:
        self.is_backing_up = False
        self.running_saved_config_id = ""
        self.set_controls_state("normal")
        self.refresh_saved_configs()
        self.update_step_buttons()
        if result == 0:
            self.progress_bar.set(1)
            self.progress_text.set("100%")
            self.status.set(self.tr("backup_success"))
            self.update_config_summary()
            messagebox.showinfo(self.tr("backup_success"), self.tr("backup_success_body"))
        else:
            self.status.set(self.tr("backup_failed"))
            detail = last_error_from_log()
            body = self.tr("backup_failed_body")
            if detail:
                body = f"{body}\n\nChi tiết gần nhất:\n{detail}"
            if "WinError 5" in detail or "Access is denied" in detail or "Không có quyền" in detail:
                body = f"{body}\n\n{self.tr('permission_hint')}"
            messagebox.showerror(self.tr("backup_failed"), body)

    def run_now(self) -> None:
        if self.is_backing_up:
            return
        if not self.save():
            return
        self.running_saved_config_id = self.selected_saved_config.get()
        self.refresh_saved_configs()
        self.is_backing_up = True
        self.set_controls_state("disabled")
        self.status.set(self.tr("backup_running"))
        self.progress_bar.set(0)
        self.progress_text.set("0%")

        def worker() -> None:
            result = run_backup(CONFIG_PATH, self.update_progress)
            self.after(0, lambda: self.finish_backup(result))

        threading.Thread(target=worker, daemon=True).start()

    def install_schedule(self) -> None:
        if not self.save():
            return
        args = ["/Create", "/F", "/TN", APP_NAME, "/TR", scheduled_command(CONFIG_PATH), "/ST", self.config_data.time]
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
        if not task_is_installed():
            self.update_schedule_status()
            messagebox.showinfo(self.tr("remove_failed"), self.tr("schedule_missing_body"))
            return
        confirmed = messagebox.askyesno(
            self.tr("remove_schedule"),
            f"Bạn có chắc muốn gỡ lịch tự động hiện tại không?\n\nTask Windows: {APP_NAME}",
        )
        if not confirmed:
            return
        result = subprocess.run(["schtasks.exe", "/Delete", "/F", "/TN", APP_NAME], text=True, capture_output=True)
        if result.returncode == 0:
            self.status.set(self.tr("removed"))
            self.update_schedule_status()
            messagebox.showinfo(self.tr("removed"), self.tr("schedule_removed_body"))
        else:
            self.status.set(self.tr("remove_failed"))
            self.update_schedule_status()
            messagebox.showwarning(self.tr("remove_failed"), result.stderr or result.stdout or self.tr("schedule_missing_body"))

    def open_log(self) -> None:
        if not LOG_PATH.exists():
            LOG_PATH.write_text("Chưa có log backup.\n", encoding="utf-8")
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
