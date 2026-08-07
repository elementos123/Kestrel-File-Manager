import os
import sys
import subprocess
import datetime
from pathlib import Path
from typing import Optional


FILE_ICONS = {
    # Folders
    "folder":    "📁",
    # Images
    ".jpg":  "🖼", ".jpeg": "🖼", ".png": "🖼", ".gif": "🖼",
    ".bmp":  "🖼", ".webp": "🖼", ".svg": "🖼", ".ico": "🖼",
    ".tiff": "🖼", ".tif":  "🖼", ".heic": "🖼", ".raw": "🖼",
    # Video
    ".mp4":  "🎬", ".mkv": "🎬", ".avi": "🎬", ".mov": "🎬",
    ".wmv":  "🎬", ".flv": "🎬", ".webm": "🎬", ".m4v": "🎬",
    # Audio
    ".mp3":  "🎵", ".wav": "🎵", ".flac": "🎵", ".ogg": "🎵",
    ".aac":  "🎵", ".m4a": "🎵", ".wma": "🎵",
    # Documents
    ".pdf":  "📕", ".doc": "📘", ".docx": "📘", ".odt": "📘",
    ".xls":  "📗", ".xlsx": "📗", ".ods": "📗",
    ".ppt":  "📙", ".pptx": "📙", ".odp": "📙",
    # Text / Code
    ".txt":  "📄", ".md": "📝", ".rst": "📝", ".log": "📄",
    ".py":   "🐍", ".js": "📜", ".ts": "📜", ".jsx": "📜", ".tsx": "📜",
    ".html": "🌐", ".htm": "🌐", ".css": "🎨", ".scss": "🎨",
    ".json": "⚙",  ".yaml": "⚙", ".yml": "⚙", ".toml": "⚙",
    ".xml":  "⚙",  ".ini": "⚙", ".cfg": "⚙", ".conf": "⚙",
    ".c":    "⚡",  ".cpp": "⚡", ".h": "⚡", ".hpp": "⚡",
    ".cs":   "⚡",  ".java": "☕", ".go": "🐹", ".rs": "🦀",
    ".rb":   "💎",  ".php": "🐘", ".sh": "🖥", ".bat": "🖥", ".ps1": "🖥",
    ".lua":  "🌙",  ".r": "📊", ".sql": "🗄",
    # Archives
    ".zip":  "🗜", ".rar": "🗜", ".7z": "🗜", ".tar": "🗜",
    ".gz":   "🗜", ".bz2": "🗜", ".xz": "🗜",
    # Executables / System
    ".exe":  "⚙", ".msi": "📦", ".dll": "🔧", ".sys": "🔧",
    ".lnk":  "🔗", ".url": "🔗",
    # Fonts
    ".ttf":  "🔤", ".otf": "🔤", ".woff": "🔤", ".woff2": "🔤",
}

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".webp", ".tiff", ".tif", ".heic",
}

TEXT_EXTENSIONS = {
    ".txt", ".md", ".rst", ".log", ".py", ".js", ".ts", ".jsx", ".tsx",
    ".html", ".htm", ".css", ".scss", ".json", ".yaml", ".yml", ".toml",
    ".xml", ".ini", ".cfg", ".conf", ".c", ".cpp", ".h", ".hpp", ".cs",
    ".java", ".go", ".rs", ".rb", ".php", ".sh", ".bat", ".ps1", ".lua",
    ".r", ".sql", ".csv", ".tsv", ".env", ".gitignore", ".dockerfile",
    ".makefile", ".cmake",
}


def get_file_icon(path: str, is_dir: bool = False) -> str:
    if is_dir:
        return FILE_ICONS["folder"]
    ext = Path(path).suffix.lower()
    return FILE_ICONS.get(ext, "📄")


def format_size(size_bytes: int) -> str:
    if size_bytes < 0:
        return ""
    if size_bytes == 0:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            if unit == "B":
                return f"{size_bytes} B"
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def format_date(timestamp: float) -> str:
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%d/%m/%Y  %H:%M")


def format_date_relative(timestamp: float) -> str:
    try:
        diff = datetime.datetime.now() - datetime.datetime.fromtimestamp(timestamp)
        s = diff.total_seconds()
        if s < 60:
            return "Hace un momento"
        if s < 3600:
            m = int(s / 60); return f"Hace {m} minuto{'s' if m != 1 else ''}"
        if s < 86400:
            h = int(s / 3600); return f"Hace {h} hora{'s' if h != 1 else ''}"
        if s < 604800:
            d = int(s / 86400); return f"Hace {d} día{'s' if d != 1 else ''}"
        if s < 2592000:
            w = int(s / 604800); return f"Hace {w} semana{'s' if w != 1 else ''}"
        if s < 31536000:
            mo = int(s / 2592000); return f"Hace {mo} mes{'es' if mo != 1 else ''}"
        y = int(s / 31536000); return f"Hace {y} año{'s' if y != 1 else ''}"
    except Exception:
        return format_date(timestamp)


def format_size_in_unit(size_bytes: int, unit: str = "auto") -> str:
    if size_bytes < 0:
        return ""
    if unit == "b":
        return f"{size_bytes:,} B"
    if unit == "kb":
        return f"{size_bytes / 1024:.1f} KB"
    if unit == "mb":
        return f"{size_bytes / 1_048_576:.1f} MB"
    if unit == "gb":
        return f"{size_bytes / 1_073_741_824:.2f} GB"
    return format_size(size_bytes)  # auto


def is_image(path: str) -> bool:
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def is_text(path: str) -> bool:
    return Path(path).suffix.lower() in TEXT_EXTENSIONS


def get_drives() -> list[str]:
    if sys.platform != "win32":
        return ["/"]
    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives


def get_drive_label(drive: str) -> str:
    if sys.platform != "win32":
        return drive
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(261)
        ctypes.windll.kernel32.GetVolumeInformationW(
            drive, buf, ctypes.sizeof(buf), None, None, None, None, 0
        )
        label = buf.value.strip()
        letter = drive.rstrip("\\")
        if label:
            return f"{label} ({letter})"
        from src.i18n import t
        return t("drive.local_disk", letter=letter)
    except Exception:
        return drive


def open_file(path: str) -> None:
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        pass


def open_in_terminal(path: str, preferred: str = "auto") -> None:
    import shutil as _sh
    cwd = path if os.path.isdir(path) else os.path.dirname(path)
    if sys.platform != "win32":
        return
    NEW_CON = subprocess.CREATE_NEW_CONSOLE
    candidates = []
    if preferred == "wt" or preferred == "auto":
        if _sh.which("wt"):
            candidates.append(["wt", "new-tab", "--startingDirectory", cwd])
    if preferred == "pwsh" or preferred == "auto":
        if _sh.which("pwsh"):
            candidates.append(["pwsh", "-NoExit", "-Command", f"Set-Location -LiteralPath '{cwd}'"])
    if preferred == "powershell" or preferred == "auto":
        candidates.append(["powershell.exe", "-NoExit", "-Command", f"Set-Location -LiteralPath '{cwd}'"])
    candidates.append(["cmd.exe", "/K", f"cd /d \"{cwd}\""])
    for cmd in candidates:
        try:
            if cmd[0] in ("wt",):
                subprocess.Popen(cmd)
            else:
                subprocess.Popen(cmd, creationflags=NEW_CON)
            return
        except Exception:
            continue


def get_user_dirs() -> dict[str, str]:
    from src.i18n import t
    home = Path.home()
    dirs = {
        t("dir.home"):      str(home),
        t("dir.desktop"):   str(home / "Desktop"),
        t("dir.downloads"): str(home / "Downloads"),
        t("dir.documents"): str(home / "Documents"),
        t("dir.pictures"):  str(home / "Pictures"),
        t("dir.music"):     str(home / "Music"),
        t("dir.videos"):    str(home / "Videos"),
    }
    return {k: v for k, v in dirs.items() if os.path.exists(v)}


ARCHIVE_EXTENSIONS = {
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tar.gz", ".tar.bz2",
}


def is_archive(path: str) -> bool:
    p = Path(path)
    return p.suffix.lower() in ARCHIVE_EXTENSIONS or "".join(p.suffixes[-2:]).lower() in ARCHIVE_EXTENSIONS


def compress_to_zip(paths: list[str], dest_dir: str) -> tuple[bool, str]:
    import zipfile
    if not paths:
        return False, "Sin archivos seleccionados"
    stem = Path(paths[0]).stem if len(paths) == 1 else Path(dest_dir).name
    zip_name = stem + ".zip"
    zip_path = os.path.join(dest_dir, zip_name)
    counter = 1
    while os.path.exists(zip_path):
        zip_path = os.path.join(dest_dir, f"{stem} ({counter}).zip")
        counter += 1
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for src in paths:
                if os.path.isfile(src):
                    zf.write(src, os.path.basename(src))
                elif os.path.isdir(src):
                    base = os.path.dirname(src)
                    for root, _dirs, files in os.walk(src):
                        for fn in files:
                            fp = os.path.join(root, fn)
                            zf.write(fp, os.path.relpath(fp, base))
        return True, zip_path
    except Exception as e:
        return False, str(e)


def extract_archive(path: str, dest_dir: str) -> tuple[bool, str]:
    try:
        import shutil as _sh
        _sh.unpack_archive(path, dest_dir)
        return True, dest_dir
    except Exception as e:
        return False, str(e)


def read_text_preview(path: str, max_bytes: int = 16_384) -> Optional[str]:
    try:
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                with open(path, "r", encoding=enc, errors="strict") as f:
                    return f.read(max_bytes)
            except (UnicodeDecodeError, UnicodeError):
                continue
        return None
    except Exception:
        return None
