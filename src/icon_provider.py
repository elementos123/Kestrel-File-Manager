"""
Centralised icon provider — wraps qtawesome so the rest of the app
never imports qtawesome directly and gracefully degrades if missing.
"""

from __future__ import annotations
from PyQt6.QtGui import QIcon

try:
    import qtawesome as _qta
    _OK = True
except ImportError:
    _OK = False


def get(name: str, color: str = "#b0b0b0",
        color_active: str | None = None,
        color_disabled: str | None = None,
        scale: float = 1.0) -> QIcon:
    if not _OK:
        return QIcon()
    try:
        opts: dict = {"color": color, "scale_factor": scale}
        if color_active:
            opts["color_active"]   = color_active
        if color_disabled:
            opts["color_disabled"] = color_disabled
        return _qta.icon(name, **opts)
    except Exception:
        return QIcon()


# ─────────────────────────────────────────────────────────
#  Convenience wrappers  (name, default neutral colour)
# ─────────────────────────────────────────────────────────

def make(name: str, c: str = "#b0b0b0", **kw) -> QIcon:
    return get(name, color=c, **kw)


# Navigation
def nav_back(c="#b0b0b0"):    return get("mdi.arrow-left-circle-outline", c)
def nav_fwd(c="#b0b0b0"):     return get("mdi.arrow-right-circle-outline", c)
def nav_up(c="#b0b0b0"):      return get("mdi.arrow-up-circle-outline",  c)
def nav_home(c="#b0b0b0"):    return get("mdi.home-outline",              c)
def refresh(c="#b0b0b0"):     return get("mdi.refresh",                   c)
def new_window(c="#b0b0b0"):  return get("mdi.window-restore",            c)

# View modes
def view_details(c="#b0b0b0"):  return get("mdi.view-list",               c)
def view_icons(c="#b0b0b0"):    return get("mdi.view-grid-outline",        c)
def view_list(c="#b0b0b0"):     return get("mdi.format-list-bulleted",     c)
def view_dual(c="#b0b0b0"):     return get("mdi.view-week-outline",        c)

# Panels & UI
def preview_icon(c="#b0b0b0"):    return get("mdi.eye-outline",            c)
def sidebar_icon(c="#b0b0b0"):    return get("mdi.view-split-vertical",    c)
def settings_icon(c="#b0b0b0"):   return get("mdi.cog-outline",            c)
def theme_dark(c="#b0b0b0"):      return get("mdi.moon-waning-crescent",   c)
def theme_light(c="#b0b0b0"):     return get("mdi.white-balance-sunny",    c)

# Search
def search_icon(c="#b0b0b0"):     return get("mdi.magnify",                c)
def search_recursive(c="#b0b0b0"):return get("mdi.folder-search-outline",  c)
def search_clear(c="#b0b0b0"):    return get("mdi.close-circle-outline",   c)
def history_icon(c="#b0b0b0"):    return get("mdi.history",                c)

# Folders / files
def folder(c="#b0b0b0"):          return get("mdi.folder-outline",         c)
def folder_open(c="#b0b0b0"):     return get("mdi.folder-open-outline",    c)
def folder_plus(c="#b0b0b0"):     return get("mdi.folder-plus-outline",    c)
def file_plus(c="#b0b0b0"):       return get("mdi.file-plus-outline",      c)
def file_icon(c="#b0b0b0"):       return get("mdi.file-outline",           c)

# Quick-access dirs
def dir_home(c="#b0b0b0"):        return get("mdi.home-outline",           c)
def dir_desktop(c="#b0b0b0"):     return get("mdi.monitor",                c)
def dir_downloads(c="#b0b0b0"):   return get("mdi.download-outline",       c)
def dir_documents(c="#b0b0b0"):   return get("mdi.file-document-outline",  c)
def dir_pictures(c="#b0b0b0"):    return get("mdi.image-outline",          c)
def dir_music(c="#b0b0b0"):       return get("mdi.music-note-outline",     c)
def dir_videos(c="#b0b0b0"):      return get("mdi.video-outline",          c)

# Sidebar misc
def drive_icon(c="#b0b0b0"):      return get("mdi.harddisk",               c)
def bookmark_icon(c="#b0b0b0"):   return get("mdi.bookmark-outline",       c)
def star_icon(c="#b0b0b0"):       return get("mdi.star-outline",           c)
def clock_icon(c="#b0b0b0"):      return get("mdi.clock-outline",          c)
def recent_file(c="#b0b0b0"):     return get("mdi.file-clock-outline",     c)

# File operations
def copy_icon(c="#b0b0b0"):       return get("mdi.content-copy",           c)
def cut_icon(c="#b0b0b0"):        return get("mdi.content-cut",            c)
def paste_icon(c="#b0b0b0"):      return get("mdi.content-paste",          c)
def delete_icon(c="#e06c75"):     return get("mdi.delete-outline",         c)
def rename_icon(c="#b0b0b0"):     return get("mdi.pencil-outline",         c)
def copy_path_icon(c="#b0b0b0"):  return get("mdi.link-variant",           c)
def properties_icon(c="#b0b0b0"): return get("mdi.information-outline",   c)
def open_with_icon(c="#b0b0b0"):  return get("mdi.application-outline",   c)
def terminal_icon(c="#b0b0b0"):   return get("mdi.console",                c)
def compress_icon(c="#b0b0b0"):   return get("mdi.zip-box-outline",        c)
def extract_icon(c="#b0b0b0"):    return get("mdi.package-variant-open",   c)
def ext_tool_icon(c="#b0b0b0"):   return get("mdi.hammer-screwdriver",     c)
def rename_multi(c="#b0b0b0"):    return get("mdi.rename-box",             c)

# Command bar
def open_icon(c="#b0b0b0"):       return get("mdi.open-in-app",            c)
def new_folder_icon(c="#b0b0b0"): return get("mdi.folder-plus-outline",   c)


# ─────────────────────────────────────────────────────────
#  Dir-name → icon mapping (used by sidebar quick access)
# ─────────────────────────────────────────────────────────

_DIR_ICON_FN = {
    "inicio":       dir_home,
    "home":         dir_home,
    "escritorio":   dir_desktop,
    "desktop":      dir_desktop,
    "descargas":    dir_downloads,
    "downloads":    dir_downloads,
    "documentos":   dir_documents,
    "documents":    dir_documents,
    "imágenes":     dir_pictures,
    "pictures":     dir_pictures,
    "música":       dir_music,
    "music":        dir_music,
    "vídeos":       dir_videos,
    "videos":       dir_videos,
}


def for_dir_label(label: str, c: str = "#b0b0b0") -> QIcon:
    """Return appropriate icon for a sidebar quick-access label."""
    key = label.lower().strip()
    fn  = _DIR_ICON_FN.get(key, folder)
    return fn(c)
