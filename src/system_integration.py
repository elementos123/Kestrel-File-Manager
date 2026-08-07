"""Optional, reversible "set as default file manager" integration.

Windows: only ever touches HKEY_CURRENT_USER\\Software\\Classes — never
HKEY_CLASSES_ROOT or HKLM. This redirects what happens when the user
double-clicks a folder/drive, same mechanism third-party explorer
replacements use; it does not touch explorer.exe itself or the taskbar/
desktop shell, and needs no admin rights. Removing the override falls
back to the system default automatically.

Linux: uses the standard freedesktop mimeapps.list mechanism for the
inode/directory MIME type. Whatever was previously set is remembered
under a private [X-Kestrel-Backup] section so it can be restored
exactly when the user turns this back off.

Every function here only runs when the user explicitly asks (a button in
Settings) — nothing here is called automatically on startup or install.
"""

import os
import sys
import shutil
import subprocess
import configparser
from pathlib import Path
from typing import Tuple

from src.logger import get_logger

_log = get_logger("system_integration")

_MIME = "inode/directory"
_DESKTOP_NAME = "kestrel.desktop"


def _app_path() -> str:
    """Absolute path to whatever should be re-launched: the AppImage file
    itself (not its ephemeral extraction dir), the frozen exe, or main.py."""
    appimage = os.environ.get("APPIMAGE")
    if appimage:
        return appimage
    if getattr(sys, "frozen", False):
        return sys.executable
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))


def is_supported() -> bool:
    return sys.platform in ("win32", "linux")


def is_default() -> bool:
    if sys.platform == "win32":
        return _is_default_windows()
    if sys.platform == "linux":
        return _is_default_linux()
    return False


def set_default() -> Tuple[bool, str]:
    if sys.platform == "win32":
        return _set_default_windows()
    if sys.platform == "linux":
        return _set_default_linux()
    return False, "Plataforma no compatible"


def unset_default() -> Tuple[bool, str]:
    if sys.platform == "win32":
        return _unset_default_windows()
    if sys.platform == "linux":
        return _unset_default_linux()
    return False, "Plataforma no compatible"


# ── Windows ──────────────────────────────────────────────────

_WIN_KEYS = (
    r"Software\Classes\Directory\shell\open\command",
    r"Software\Classes\Drive\shell\open\command",
)

# "My Computer"'s shell verb — Win+E invokes this CLSID's opennewwindow verb
# rather than launching explorer.exe by a hardcoded path, so overriding it
# (per-user, like everything else here) redirects Win+E too. Unlike the
# Directory/Drive keys, the *unmodified* system version of this key carries
# a DelegateExecute value that takes priority over a plain command string —
# our override key must NOT have one, so Windows falls back to running our
# command string directly instead.
_MY_COMPUTER_KEY = (
    r"Software\Classes\CLSID\{20D04FE0-3AEA-1069-A2D8-08002B30309D}\shell\opennewwindow\command"
)


def _win_command(with_arg: bool = True) -> str:
    path = _app_path()
    exe = path if (getattr(sys, "frozen", False) or os.environ.get("APPIMAGE")) else None
    prefix = f'"{path}"' if exe else f'"{sys.executable}" "{path}"'
    return f'{prefix} "%1"' if with_arg else prefix


def _is_default_windows() -> bool:
    import winreg
    cmd = _win_command(with_arg=True)
    cmd_no_arg = _win_command(with_arg=False)
    try:
        for key_path in _WIN_KEYS:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as k:
                value, _ = winreg.QueryValueEx(k, "")
                if value != cmd:
                    return False
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _MY_COMPUTER_KEY) as k:
            value, _ = winreg.QueryValueEx(k, "")
            if value != cmd_no_arg:
                return False
        return True
    except FileNotFoundError:
        return False
    except OSError:
        _log.exception("Failed to read default-file-manager registry state")
        return False


def _set_default_windows() -> Tuple[bool, str]:
    import winreg
    cmd = _win_command(with_arg=True)
    try:
        for key_path in _WIN_KEYS:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as k:
                winreg.SetValueEx(k, "", 0, winreg.REG_SZ, cmd)

        # Win+E: create fresh (no inherited DelegateExecute) and set only
        # the plain command string.
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _MY_COMPUTER_KEY) as k:
            winreg.SetValueEx(k, "", 0, winreg.REG_SZ, _win_command(with_arg=False))
            try:
                winreg.DeleteValue(k, "DelegateExecute")
            except FileNotFoundError:
                pass
        return True, ""
    except OSError as e:
        _log.exception("Failed to set Kestrel as default file manager")
        return False, str(e)


def _unset_default_windows() -> Tuple[bool, str]:
    import winreg
    try:
        for key_path in _WIN_KEYS + (_MY_COMPUTER_KEY,):
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except FileNotFoundError:
                pass
        return True, ""
    except OSError as e:
        _log.exception("Failed to unset Kestrel as default file manager")
        return False, str(e)


# ── Linux ────────────────────────────────────────────────────

def _apps_dir() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "applications"


def _desktop_file() -> Path:
    return _apps_dir() / _DESKTOP_NAME


def _mimeapps_path() -> Path:
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return config_home / "mimeapps.list"


def _linux_exec_line() -> str:
    path = _app_path()
    if getattr(sys, "frozen", False) or os.environ.get("APPIMAGE"):
        return f'"{path}" %f'
    return f'"{sys.executable}" "{path}" %f'


def _ensure_desktop_file():
    _apps_dir().mkdir(parents=True, exist_ok=True)
    content = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Kestrel\n"
        "GenericName=File Manager\n"
        "Comment=Explorador de archivos de alto rendimiento para usuarios avanzados\n"
        f"Exec={_linux_exec_line()}\n"
        "Icon=kestrel\n"
        "Categories=Utility;FileManager;System;\n"
        "Terminal=false\n"
        "StartupWMClass=Kestrel\n"
        f"MimeType={_MIME};\n"
    )
    _desktop_file().write_text(content, encoding="utf-8")
    os.chmod(_desktop_file(), 0o755)


def _read_mimeapps() -> configparser.ConfigParser:
    cp = configparser.ConfigParser(strict=False, interpolation=None)
    path = _mimeapps_path()
    if path.exists():
        cp.read(path, encoding="utf-8")
    return cp


def _write_mimeapps(cp: configparser.ConfigParser):
    path = _mimeapps_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        cp.write(f)


def _is_default_linux() -> bool:
    cp = _read_mimeapps()
    current = cp.get("Default Applications", _MIME, fallback="").strip().rstrip(";")
    return current == _DESKTOP_NAME


def _set_default_linux() -> Tuple[bool, str]:
    try:
        _ensure_desktop_file()
        cp = _read_mimeapps()
        if not cp.has_section("Default Applications"):
            cp.add_section("Default Applications")

        previous = cp.get("Default Applications", _MIME, fallback="").strip().rstrip(";")
        if previous and previous != _DESKTOP_NAME:
            if not cp.has_section("X-Kestrel-Backup"):
                cp.add_section("X-Kestrel-Backup")
            cp.set("X-Kestrel-Backup", _MIME, previous)

        cp.set("Default Applications", _MIME, _DESKTOP_NAME)
        _write_mimeapps(cp)

        if shutil.which("xdg-mime"):
            subprocess.run(["xdg-mime", "default", _DESKTOP_NAME, _MIME], check=False)
        return True, ""
    except Exception as e:
        _log.exception("Failed to set Kestrel as default file manager")
        return False, str(e)


def _unset_default_linux() -> Tuple[bool, str]:
    try:
        cp = _read_mimeapps()
        restore = ""
        if cp.has_section("X-Kestrel-Backup"):
            restore = cp.get("X-Kestrel-Backup", _MIME, fallback="").strip()
            cp.remove_option("X-Kestrel-Backup", _MIME)

        if cp.has_section("Default Applications"):
            if restore:
                cp.set("Default Applications", _MIME, restore)
            else:
                cp.remove_option("Default Applications", _MIME)

        _write_mimeapps(cp)

        if shutil.which("xdg-mime"):
            target = restore or "nautilus.desktop"
            if restore:
                subprocess.run(["xdg-mime", "default", target, _MIME], check=False)
        return True, ""
    except Exception as e:
        _log.exception("Failed to unset Kestrel as default file manager")
        return False, str(e)
