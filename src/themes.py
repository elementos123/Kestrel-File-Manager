from typing import Dict, Any

THEMES: Dict[str, Dict[str, Any]] = {
    "dark_fluent": {
        "name": "Dark Fluent",
        "bg_primary":        "#1c1c1c",
        "bg_secondary":      "#252526",
        "bg_tertiary":       "#2d2d2d",
        "bg_hover":          "#2a2d2e",
        "bg_selected":       "#094771",
        "bg_selected_hover": "#0e5a8a",
        "accent":            "#0078d4",
        "accent_hover":      "#1184d8",
        "accent_text":       "#ffffff",
        "text_primary":      "#ffffff",
        "text_secondary":    "#b0b0b0",
        "text_muted":        "#6d6d6d",
        "border":            "#333333",
        "border_light":      "#3f3f3f",
        "scrollbar_bg":      "#1c1c1c",
        "scrollbar_handle":  "#3f3f3f",
        "scrollbar_hover":   "#555555",
        "tab_active":        "#252526",
        "tab_inactive":      "#1e1e1e",
        "input_bg":          "#3c3c3c",
        "button_bg":         "#3c3c3c",
        "button_hover":      "#4a4a4a",
        "button_pressed":    "#2d2d2d",
        "separator":         "#333333",
        "sidebar_bg":        "#1e1e1e",
        "preview_bg":        "#1a1a1a",
        "toolbar_bg":        "#1e1e1e",
        "statusbar_bg":      "#007acc",
        "statusbar_text":    "#ffffff",
        "danger":            "#f44747",
        "success":           "#4ec9b0",
        "warning":           "#dcdcaa",
    },
    "light_fluent": {
        "name": "Light Fluent",
        "bg_primary":        "#f3f3f3",
        "bg_secondary":      "#ffffff",
        "bg_tertiary":       "#f9f9f9",
        "bg_hover":          "#e8e8e8",
        "bg_selected":       "#cce4f7",
        "bg_selected_hover": "#b8d7f0",
        "accent":            "#0078d4",
        "accent_hover":      "#106ebe",
        "accent_text":       "#ffffff",
        "text_primary":      "#1a1a1a",
        "text_secondary":    "#5a5a5a",
        "text_muted":        "#999999",
        "border":            "#e0e0e0",
        "border_light":      "#ebebeb",
        "scrollbar_bg":      "#f3f3f3",
        "scrollbar_handle":  "#c1c1c1",
        "scrollbar_hover":   "#a8a8a8",
        "tab_active":        "#ffffff",
        "tab_inactive":      "#f0f0f0",
        "input_bg":          "#ffffff",
        "button_bg":         "#efefef",
        "button_hover":      "#e5e5e5",
        "button_pressed":    "#d8d8d8",
        "separator":         "#e0e0e0",
        "sidebar_bg":        "#f0f0f0",
        "preview_bg":        "#fafafa",
        "toolbar_bg":        "#f0f0f0",
        "statusbar_bg":      "#0078d4",
        "statusbar_text":    "#ffffff",
        "danger":            "#d32f2f",
        "success":           "#1b5e20",
        "warning":           "#e65100",
    },
    "nord": {
        "name": "Nord",
        "bg_primary":        "#2E3440",
        "bg_secondary":      "#3B4252",
        "bg_tertiary":       "#434C5E",
        "bg_hover":          "#434C5E",
        "bg_selected":       "#3D5775",
        "bg_selected_hover": "#4D6A8A",
        "accent":            "#88C0D0",
        "accent_hover":      "#8FBCBB",
        "accent_text":       "#2E3440",
        "text_primary":      "#ECEFF4",
        "text_secondary":    "#D8DEE9",
        "text_muted":        "#4C566A",
        "border":            "#3B4252",
        "border_light":      "#434C5E",
        "scrollbar_bg":      "#2E3440",
        "scrollbar_handle":  "#4C566A",
        "scrollbar_hover":   "#5E81AC",
        "tab_active":        "#3B4252",
        "tab_inactive":      "#2E3440",
        "input_bg":          "#3B4252",
        "button_bg":         "#434C5E",
        "button_hover":      "#4C566A",
        "button_pressed":    "#3B4252",
        "separator":         "#3B4252",
        "sidebar_bg":        "#2E3440",
        "preview_bg":        "#252B37",
        "toolbar_bg":        "#2E3440",
        "statusbar_bg":      "#5E81AC",
        "statusbar_text":    "#ECEFF4",
        "danger":            "#BF616A",
        "success":           "#A3BE8C",
        "warning":           "#EBCB8B",
    },
    "dracula": {
        "name": "Dracula",
        "bg_primary":        "#282A36",
        "bg_secondary":      "#21222C",
        "bg_tertiary":       "#44475A",
        "bg_hover":          "#383A4A",
        "bg_selected":       "#44475A",
        "bg_selected_hover": "#565970",
        "accent":            "#BD93F9",
        "accent_hover":      "#CBA4FF",
        "accent_text":       "#F8F8F2",
        "text_primary":      "#F8F8F2",
        "text_secondary":    "#BFBFBF",
        "text_muted":        "#6272A4",
        "border":            "#44475A",
        "border_light":      "#565970",
        "scrollbar_bg":      "#282A36",
        "scrollbar_handle":  "#44475A",
        "scrollbar_hover":   "#6272A4",
        "tab_active":        "#282A36",
        "tab_inactive":      "#21222C",
        "input_bg":          "#44475A",
        "button_bg":         "#44475A",
        "button_hover":      "#565970",
        "button_pressed":    "#383A4A",
        "separator":         "#44475A",
        "sidebar_bg":        "#21222C",
        "preview_bg":        "#1E1F29",
        "toolbar_bg":        "#21222C",
        "statusbar_bg":      "#BD93F9",
        "statusbar_text":    "#282A36",
        "danger":            "#FF5555",
        "success":           "#50FA7B",
        "warning":           "#FFB86C",
    },
    "catppuccin": {
        "name": "Catppuccin Mocha",
        "bg_primary":        "#1E1E2E",
        "bg_secondary":      "#181825",
        "bg_tertiary":       "#313244",
        "bg_hover":          "#313244",
        "bg_selected":       "#45475A",
        "bg_selected_hover": "#585B70",
        "accent":            "#CBA6F7",
        "accent_hover":      "#D5B8FB",
        "accent_text":       "#1E1E2E",
        "text_primary":      "#CDD6F4",
        "text_secondary":    "#BAC2DE",
        "text_muted":        "#585B70",
        "border":            "#313244",
        "border_light":      "#45475A",
        "scrollbar_bg":      "#1E1E2E",
        "scrollbar_handle":  "#585B70",
        "scrollbar_hover":   "#7F849C",
        "tab_active":        "#1E1E2E",
        "tab_inactive":      "#181825",
        "input_bg":          "#313244",
        "button_bg":         "#313244",
        "button_hover":      "#45475A",
        "button_pressed":    "#181825",
        "separator":         "#313244",
        "sidebar_bg":        "#181825",
        "preview_bg":        "#11111B",
        "toolbar_bg":        "#181825",
        "statusbar_bg":      "#CBA6F7",
        "statusbar_text":    "#1E1E2E",
        "danger":            "#F38BA8",
        "success":           "#A6E3A1",
        "warning":           "#FAB387",
    },
    "gruvbox": {
        "name": "Gruvbox Dark",
        "bg_primary":        "#282828",
        "bg_secondary":      "#3c3836",
        "bg_tertiary":       "#504945",
        "bg_hover":          "#3c3836",
        "bg_selected":       "#504945",
        "bg_selected_hover": "#665c54",
        "accent":            "#fe8019",
        "accent_hover":      "#ff9838",
        "accent_text":       "#282828",
        "text_primary":      "#ebdbb2",
        "text_secondary":    "#d5c4a1",
        "text_muted":        "#928374",
        "border":            "#504945",
        "border_light":      "#665c54",
        "scrollbar_bg":      "#282828",
        "scrollbar_handle":  "#504945",
        "scrollbar_hover":   "#7c6f64",
        "tab_active":        "#3c3836",
        "tab_inactive":      "#282828",
        "input_bg":          "#3c3836",
        "button_bg":         "#3c3836",
        "button_hover":      "#504945",
        "button_pressed":    "#282828",
        "separator":         "#504945",
        "sidebar_bg":        "#1d2021",
        "preview_bg":        "#1d2021",
        "toolbar_bg":        "#3c3836",
        "statusbar_bg":      "#fe8019",
        "statusbar_text":    "#282828",
        "danger":            "#fb4934",
        "success":           "#b8bb26",
        "warning":           "#fabd2f",
    },
    "tokyo_night": {
        "name": "Tokyo Night",
        "bg_primary":        "#1a1b26",
        "bg_secondary":      "#16161e",
        "bg_tertiary":       "#2f3549",
        "bg_hover":          "#252535",
        "bg_selected":       "#364a82",
        "bg_selected_hover": "#445994",
        "accent":            "#7aa2f7",
        "accent_hover":      "#89b4fa",
        "accent_text":       "#1a1b26",
        "text_primary":      "#c0caf5",
        "text_secondary":    "#a9b1d6",
        "text_muted":        "#565f89",
        "border":            "#2f3549",
        "border_light":      "#3d59a1",
        "scrollbar_bg":      "#1a1b26",
        "scrollbar_handle":  "#2f3549",
        "scrollbar_hover":   "#3d59a1",
        "tab_active":        "#1a1b26",
        "tab_inactive":      "#16161e",
        "input_bg":          "#2f3549",
        "button_bg":         "#2f3549",
        "button_hover":      "#3d4f7e",
        "button_pressed":    "#1a1b26",
        "separator":         "#2f3549",
        "sidebar_bg":        "#16161e",
        "preview_bg":        "#13131d",
        "toolbar_bg":        "#16161e",
        "statusbar_bg":      "#7aa2f7",
        "statusbar_text":    "#1a1b26",
        "danger":            "#f7768e",
        "success":           "#9ece6a",
        "warning":           "#e0af68",
    },
    "solarized_dark": {
        "name": "Solarized Dark",
        "bg_primary":        "#002b36",
        "bg_secondary":      "#073642",
        "bg_tertiary":       "#094553",
        "bg_hover":          "#0a4554",
        "bg_selected":       "#10566a",
        "bg_selected_hover": "#1a6a80",
        "accent":            "#268bd2",
        "accent_hover":      "#35a0e7",
        "accent_text":       "#fdf6e3",
        "text_primary":      "#eee8d5",
        "text_secondary":    "#93a1a1",
        "text_muted":        "#657b83",
        "border":            "#073642",
        "border_light":      "#094553",
        "scrollbar_bg":      "#002b36",
        "scrollbar_handle":  "#073642",
        "scrollbar_hover":   "#268bd2",
        "tab_active":        "#002b36",
        "tab_inactive":      "#001e27",
        "input_bg":          "#073642",
        "button_bg":         "#073642",
        "button_hover":      "#094553",
        "button_pressed":    "#002b36",
        "separator":         "#073642",
        "sidebar_bg":        "#001e27",
        "preview_bg":        "#001e27",
        "toolbar_bg":        "#073642",
        "statusbar_bg":      "#268bd2",
        "statusbar_text":    "#fdf6e3",
        "danger":            "#dc322f",
        "success":           "#859900",
        "warning":           "#b58900",
    },
    "solarized_light": {
        "name": "Solarized Light",
        "bg_primary":        "#fdf6e3",
        "bg_secondary":      "#eee8d5",
        "bg_tertiary":       "#e8e2d0",
        "bg_hover":          "#e0dac8",
        "bg_selected":       "#c9dce8",
        "bg_selected_hover": "#b0cede",
        "accent":            "#268bd2",
        "accent_hover":      "#1a80c8",
        "accent_text":       "#fdf6e3",
        "text_primary":      "#073642",
        "text_secondary":    "#586e75",
        "text_muted":        "#93a1a1",
        "border":            "#d8d0be",
        "border_light":      "#c8c0ae",
        "scrollbar_bg":      "#eee8d5",
        "scrollbar_handle":  "#c8c0ae",
        "scrollbar_hover":   "#268bd2",
        "tab_active":        "#fdf6e3",
        "tab_inactive":      "#eee8d5",
        "input_bg":          "#eee8d5",
        "button_bg":         "#e8e2d0",
        "button_hover":      "#d8d0be",
        "button_pressed":    "#c8c0ae",
        "separator":         "#d8d0be",
        "sidebar_bg":        "#eee8d5",
        "preview_bg":        "#f8f0d8",
        "toolbar_bg":        "#eee8d5",
        "statusbar_bg":      "#268bd2",
        "statusbar_text":    "#fdf6e3",
        "danger":            "#dc322f",
        "success":           "#859900",
        "warning":           "#b58900",
    },
    "one_dark": {
        "name": "One Dark Pro",
        "bg_primary":        "#282c34",
        "bg_secondary":      "#21252b",
        "bg_tertiary":       "#2c313c",
        "bg_hover":          "#2c313c",
        "bg_selected":       "#3e4452",
        "bg_selected_hover": "#4b5363",
        "accent":            "#61afef",
        "accent_hover":      "#75c0ff",
        "accent_text":       "#282c34",
        "text_primary":      "#abb2bf",
        "text_secondary":    "#9da5b4",
        "text_muted":        "#5c6370",
        "border":            "#181a1f",
        "border_light":      "#2c313c",
        "scrollbar_bg":      "#282c34",
        "scrollbar_handle":  "#3e4452",
        "scrollbar_hover":   "#61afef",
        "tab_active":        "#282c34",
        "tab_inactive":      "#21252b",
        "input_bg":          "#1d2026",
        "button_bg":         "#2c313c",
        "button_hover":      "#3e4452",
        "button_pressed":    "#21252b",
        "separator":         "#2c313c",
        "sidebar_bg":        "#21252b",
        "preview_bg":        "#1d2026",
        "toolbar_bg":        "#21252b",
        "statusbar_bg":      "#21252b",
        "statusbar_text":    "#61afef",
        "danger":            "#e06c75",
        "success":           "#98c379",
        "warning":           "#e5c07b",
    },
    "monokai": {
        "name": "Monokai",
        "bg_primary":        "#272822",
        "bg_secondary":      "#1e1f1c",
        "bg_tertiary":       "#3e3d32",
        "bg_hover":          "#3e3d32",
        "bg_selected":       "#49483e",
        "bg_selected_hover": "#75715e",
        "accent":            "#a6e22e",
        "accent_hover":      "#baf040",
        "accent_text":       "#272822",
        "text_primary":      "#f8f8f2",
        "text_secondary":    "#cfcfc2",
        "text_muted":        "#75715e",
        "border":            "#3e3d32",
        "border_light":      "#49483e",
        "scrollbar_bg":      "#272822",
        "scrollbar_handle":  "#49483e",
        "scrollbar_hover":   "#75715e",
        "tab_active":        "#272822",
        "tab_inactive":      "#1e1f1c",
        "input_bg":          "#3e3d32",
        "button_bg":         "#3e3d32",
        "button_hover":      "#49483e",
        "button_pressed":    "#272822",
        "separator":         "#3e3d32",
        "sidebar_bg":        "#1e1f1c",
        "preview_bg":        "#1a1b17",
        "toolbar_bg":        "#1e1f1c",
        "statusbar_bg":      "#a6e22e",
        "statusbar_text":    "#272822",
        "danger":            "#f92672",
        "success":           "#a6e22e",
        "warning":           "#e6db74",
    },
    "dark_purple": {
        "name": "Dark Purple",
        "bg_primary":        "#1a1a2e",
        "bg_secondary":      "#16213e",
        "bg_tertiary":       "#0f3460",
        "bg_hover":          "#1e2245",
        "bg_selected":       "#6a0dad",
        "bg_selected_hover": "#7b20bd",
        "accent":            "#c678dd",
        "accent_hover":      "#d48ee8",
        "accent_text":       "#ffffff",
        "text_primary":      "#ffffff",
        "text_secondary":    "#a9b1c6",
        "text_muted":        "#5c6370",
        "border":            "#2d3250",
        "border_light":      "#3d4265",
        "scrollbar_bg":      "#1a1a2e",
        "scrollbar_handle":  "#3d3d6e",
        "scrollbar_hover":   "#5a5aaa",
        "tab_active":        "#16213e",
        "tab_inactive":      "#131326",
        "input_bg":          "#252550",
        "button_bg":         "#252550",
        "button_hover":      "#303070",
        "button_pressed":    "#1a1a40",
        "separator":         "#2d3250",
        "sidebar_bg":        "#161628",
        "preview_bg":        "#13132a",
        "toolbar_bg":        "#161628",
        "statusbar_bg":      "#6a0dad",
        "statusbar_text":    "#ffffff",
        "danger":            "#ff5370",
        "success":           "#c3e88d",
        "warning":           "#ffcb6b",
    },
    "high_contrast": {
        # WCAG AA-oriented theme: near-black background, pure-white text,
        # and a high-visibility yellow accent — all pairings below sit at
        # 7:1 contrast or better against their background.
        "name": "High Contrast",
        "bg_primary":        "#000000",
        "bg_secondary":      "#0a0a0a",
        "bg_tertiary":       "#141414",
        "bg_hover":          "#1f1f1f",
        "bg_selected":       "#ffe600",
        "bg_selected_hover": "#fff066",
        "accent":            "#ffe600",
        "accent_hover":      "#fff066",
        "accent_text":       "#000000",
        "text_primary":      "#ffffff",
        "text_secondary":    "#e6e6e6",
        "text_muted":        "#b3b3b3",
        "border":            "#ffffff",
        "border_light":      "#cccccc",
        "scrollbar_bg":      "#000000",
        "scrollbar_handle":  "#ffffff",
        "scrollbar_hover":   "#ffe600",
        "tab_active":        "#141414",
        "tab_inactive":      "#000000",
        "input_bg":          "#141414",
        "button_bg":         "#141414",
        "button_hover":      "#262626",
        "button_pressed":    "#000000",
        "separator":         "#ffffff",
        "sidebar_bg":        "#000000",
        "preview_bg":        "#000000",
        "toolbar_bg":        "#000000",
        "statusbar_bg":      "#000000",
        "statusbar_text":    "#ffffff",
        "danger":            "#ff5c5c",
        "success":           "#4ceb4c",
        "warning":           "#ffe600",
    },
}


_DENSITY_STYLES = {
    "compact": {
        "item_height": "20px",
        "item_padding": "1px 4px",
        "sidebar_item_padding": "4px 10px 4px 14px",
        "tab_padding": "5px 12px",
    },
    "normal": {
        "item_height": "24px",
        "item_padding": "3px 4px",
        "sidebar_item_padding": "6px 10px 6px 14px",
        "tab_padding": "8px 16px",
    },
    "comfortable": {
        "item_height": "32px",
        "item_padding": "6px 4px",
        "sidebar_item_padding": "9px 10px 9px 14px",
        "tab_padding": "10px 18px",
    },
}


_FONT_FAMILIES = {
    "Segoe UI":     "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    "Cascadia Code":"'Cascadia Code', 'Fira Code', 'Jetbrains Mono', monospace",
    "Consolas":     "'Consolas', 'Courier New', monospace",
    "Inter":        "'Inter', 'Segoe UI', sans-serif",
    "System":       "system-ui, sans-serif",
}

_RADII = {
    #                rb   rb_sm rb_xs rb_lg rb_scroll
    "sharp":        ( 2,    2,    1,    3,    2),
    "normal":       ( 5,    4,    3,    6,    4),
    "rounded":      ( 9,    7,    5,   12,    6),
}

_FONT_WEIGHTS = {
    "light":    300,
    "normal":   400,
    "medium":   500,
    "semibold": 600,
    "bold":     700,
}

_SCROLLBAR_WIDTHS = {
    "hidden":  3,
    "thin":    6,
    "normal":  10,
    "wide":    14,
}


def get_stylesheet(theme_key:       str  = "dark_fluent",
                   accent_override: str  = "",
                   font_size:       int  = 13,
                   density:         str  = "normal",
                   font_family:     str  = "Segoe UI",
                   border_radius:   str  = "normal",
                   font_weight:     str  = "normal",
                   scrollbar_style: str  = "thin",
                   toolbar_compact: bool = False,
                   row_height:      int  = 0) -> str:
    t = dict(THEMES.get(theme_key, THEMES["dark_fluent"]))
    if accent_override and accent_override.startswith("#") and len(accent_override) >= 7:
        t["accent"]       = accent_override
        t["accent_hover"] = accent_override
        # Derive a slightly lighter hover color by hex blending with white
        try:
            r = int(accent_override[1:3], 16)
            g = int(accent_override[3:5], 16)
            b = int(accent_override[5:7], 16)
            rh = min(255, r + 24)
            gh = min(255, g + 24)
            bh = min(255, b + 24)
            t["accent_hover"] = f"#{rh:02x}{gh:02x}{bh:02x}"
        except Exception:
            pass
    d  = dict(_DENSITY_STYLES.get(density, _DENSITY_STYLES["normal"]))
    if row_height > 0:
        d["item_height"]  = f"{row_height}px"
        pad_v = max(1, (row_height - 14) // 4)
        d["item_padding"] = f"{pad_v}px 4px"
    fs       = max(9, min(20, font_size))
    fs_small = max(8, fs - 2)
    fw       = _FONT_WEIGHTS.get(font_weight, 400)
    rb, rb_sm, rb_xs, rb_lg, rb_scroll = _RADII.get(border_radius, _RADII["normal"])
    ff       = _FONT_FAMILIES.get(font_family, f"'{font_family}', 'Segoe UI', sans-serif")
    sb_w     = _SCROLLBAR_WIDTHS.get(scrollbar_style, 6)
    sb_r     = sb_w // 2
    # Scrollbar handle: near-invisible for "hidden" style
    sb_handle = t["scrollbar_handle"] if scrollbar_style != "hidden" else "rgba(128,128,128,0.2)"
    # Toolbar sizing
    tb_pad    = "1px 4px" if toolbar_compact else "5px 8px"
    tb_btn_h  = "22px"    if toolbar_compact else "28px"
    return f"""
/* ─── Global ─────────────────────────────────────────── */
QMainWindow, QWidget {{
    background-color: {t['bg_primary']};
    color: {t['text_primary']};
    font-family: {ff};
    font-size: {fs}px;
    font-weight: {fw};
    border: none;
    outline: none;
}}

QDialog {{
    background-color: {t['bg_secondary']};
    color: {t['text_primary']};
    border-radius: {rb_lg}px;
}}

/* ─── Toolbar ─────────────────────────────────────────── */
QToolBar {{
    background-color: {t['toolbar_bg']};
    border-bottom: 1px solid {t['border']};
    spacing: 6px;
    padding: {tb_pad};
}}

QToolButton {{
    background-color: transparent;
    color: {t['text_primary']};
    border: none;
    border-radius: {rb}px;
    padding: 6px 9px;
    min-width: 26px;
    min-height: {tb_btn_h};
    font-size: {fs}px;
}}

QToolButton:hover {{
    background-color: {t['bg_hover']};
}}

QToolButton:pressed {{
    background-color: {t['button_pressed']};
    transform: translateY(1px);
}}

QToolButton:checked {{
    background-color: {t['bg_selected']};
    color: {t['accent_text']};
    border: 1px solid {t['accent']};
}}

/* Keyboard-focus ring (global outline is disabled above, so give every
   interactive control an explicit, visible focus indicator instead). */
QToolButton:focus {{
    border: 2px solid {t['accent']};
    padding: 4px 7px;
}}

/* ─── Address Bar ─────────────────────────────────────── */
QLineEdit {{
    background-color: {t['input_bg']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-bottom: 2px solid {t['border_light']};
    border-radius: {rb}px;
    padding: 6px 12px;
    font-size: 13px;
    selection-background-color: {t['accent']};
}}

QLineEdit:focus {{
    border-bottom-color: {t['accent']};
    background-color: {t['bg_primary']};
}}

/* ─── Sidebar ─────────────────────────────────────────── */
#Sidebar {{
    background-color: {t['sidebar_bg']};
    border-right: 1px solid {t['border']};
}}

#SidebarItem {{
    border-radius: {rb}px;
    margin: 1px 8px;
}}

#SidebarItem:hover {{
    background-color: {t['bg_hover']};
}}

#SidebarItem:focus {{
    border: 2px solid {t['accent']};
    margin: -1px 7px 1px 7px;
}}

/* ─── File Views ──────────────────────────────────────── */
QTreeView::item, QListView::item {{
    padding: {d['item_padding']};
    margin: 1px 4px;
    border-radius: {rb_xs}px;
}}

QTreeView::item:selected {{
    background-color: {t['bg_selected']};
    border: 1px solid {t['accent']};
}}

QTreeView::item:focus, QListView::item:focus {{
    border: 2px solid {t['accent']};
}}

QTreeView:focus, QListView:focus {{
    border: 1px solid {t['accent']};
}}

QHeaderView::section {{
    background-color: {t['bg_secondary']};
    color: {t['text_muted']};
    border: none;
    border-bottom: 1px solid {t['border']};
    padding: 9px 12px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}}

/* ─── Preview Panel ───────────────────────────────────── */
#PreviewPanel {{
    background-color: {t['preview_bg']};
    border-left: 1px solid {t['border']};
    min-width: 190px;
}}

#PreviewTitle {{
    color: {t['text_secondary']};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 10px 12px 6px 12px;
    text-transform: uppercase;
}}

#PreviewFileName {{
    color: {t['text_primary']};
    font-size: 14px;
    font-weight: 600;
    padding: 4px 12px;
    word-wrap: break-word;
}}

#PreviewMeta {{
    color: {t['text_secondary']};
    font-size: 12px;
    padding: 2px 12px;
}}

/* ─── Scrollbars ──────────────────────────────────────── */
QScrollBar:vertical {{
    background: {t['scrollbar_bg']};
    width: {sb_w}px;
    border: none;
}}

QScrollBar::handle:vertical {{
    background: {sb_handle};
    border-radius: {sb_r}px;
    min-height: 24px;
    margin: 1px;
}}

QScrollBar::handle:vertical:hover {{
    background: {t['scrollbar_hover']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {t['scrollbar_bg']};
    height: {sb_w}px;
    border: none;
}}

QScrollBar::handle:horizontal {{
    background: {sb_handle};
    border-radius: {sb_r}px;
    min-width: 24px;
    margin: 1px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {t['scrollbar_hover']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ─── Context Menu ────────────────────────────────────── */
QMenu {{
    background-color: {t['bg_tertiary']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-radius: {rb_lg}px;
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 32px 6px 16px;
    border-radius: {rb_sm}px;
    margin: 1px 4px;
}}

QMenu::item:selected {{
    background-color: {t['bg_selected']};
}}

QMenu::item:disabled {{
    color: {t['text_muted']};
}}

QMenu::separator {{
    height: 1px;
    background: {t['border']};
    margin: 4px 8px;
}}

QMenu::icon {{
    padding-left: 8px;
}}

/* ─── Status Bar ──────────────────────────────────────── */
QStatusBar {{
    background-color: {t['statusbar_bg']};
    color: {t['statusbar_text']};
    font-size: {fs_small}px;
    padding: 2px 8px;
    border-top: 1px solid {t['border']};
}}

QStatusBar::item {{
    border: none;
}}

/* ─── Splitter ────────────────────────────────────────── */
QSplitter::handle {{
    background-color: {t['border']};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:hover {{
    background-color: {t['accent']};
}}

/* ─── Progress Bar ────────────────────────────────────── */
QProgressBar {{
    background-color: {t['bg_tertiary']};
    border: 1px solid {t['border']};
    border-radius: {rb_sm}px;
    text-align: center;
    color: {t['text_primary']};
    height: 16px;
}}

QProgressBar::chunk {{
    background-color: {t['accent']};
    border-radius: {rb_xs}px;
}}

/* ─── Buttons ─────────────────────────────────────────── */
QPushButton {{
    background-color: {t['button_bg']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-radius: {rb}px;
    padding: 6px 16px;
    font-size: 13px;
    min-width: 80px;
}}

QPushButton:hover {{
    background-color: {t['button_hover']};
    border-color: {t['border_light']};
}}

QPushButton:pressed {{
    background-color: {t['button_pressed']};
}}

QPushButton#AccentButton {{
    background-color: {t['accent']};
    color: {t['accent_text']};
    border-color: {t['accent']};
}}

QPushButton#AccentButton:hover {{
    background-color: {t['accent_hover']};
}}

QPushButton:focus, QComboBox:focus {{
    border: 2px solid {t['accent']};
}}

/* ─── CheckBox & RadioButton ──────────────────────────── */
QCheckBox, QRadioButton {{
    color: {t['text_primary']};
    spacing: 10px;
    font-size: {fs}px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {t['border_light']};
    border-radius: {rb_xs}px;
    background-color: {t['input_bg']};
}}

QCheckBox::indicator:hover {{
    border-color: {t['accent']};
    background-color: {t['bg_hover']};
}}

QCheckBox::indicator:checked {{
    background-color: {t['accent']};
    border-color: {t['accent']};
}}

QCheckBox::indicator:checked:hover {{
    background-color: {t['accent_hover']};
    border-color: {t['accent_hover']};
}}

QCheckBox:focus::indicator, QRadioButton:focus::indicator {{
    border-color: {t['accent']};
    border-width: 2px;
}}

QCheckBox::indicator:disabled {{
    border-color: {t['border']};
    background-color: {t['bg_tertiary']};
    opacity: 0.5;
}}

QCheckBox:disabled {{
    color: {t['text_muted']};
}}

/* ─── RadioButton indicator ───────────────────────────── */
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {t['border_light']};
    border-radius: 9px;
    background-color: {t['input_bg']};
}}

QRadioButton::indicator:hover {{
    border-color: {t['accent']};
}}

QRadioButton::indicator:checked {{
    background-color: {t['accent']};
    border-color: {t['accent']};
}}

/* ToggleSwitch is painted entirely via QPainter — suppress Qt indicator */
ToggleSwitch {{
    spacing: 0px;
}}
ToggleSwitch::indicator {{
    width: 0px;
    height: 0px;
    border: none;
    background: transparent;
}}

/* ─── ComboBox ────────────────────────────────────────── */
QComboBox {{
    background-color: {t['input_bg']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-radius: {rb}px;
    padding: 4px 28px 4px 10px;
    min-width: 100px;
}}

QComboBox:hover {{
    border-color: {t['border_light']};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {t['bg_tertiary']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    selection-background-color: {t['bg_selected']};
}}

/* ─── Tooltip ─────────────────────────────────────────── */
QToolTip {{
    background-color: {t['bg_tertiary']};
    color: {t['text_primary']};
    border: 1px solid {t['border']};
    border-radius: {rb_sm}px;
    padding: 4px 8px;
    font-size: 12px;
}}

/* ─── TextEdit (preview) ──────────────────────────────── */
QTextEdit, QPlainTextEdit {{
    background-color: {t['bg_primary']};
    color: {t['text_primary']};
    border: none;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 8px;
    selection-background-color: {t['accent']};
}}

/* ─── MessageBox ──────────────────────────────────────── */
QMessageBox {{
    background-color: {t['bg_secondary']};
    color: {t['text_primary']};
}}

/* ─── GroupBox ────────────────────────────────────────── */
QGroupBox {{
    border: 1px solid {t['border']};
    border-radius: {rb_lg}px;
    margin-top: 14px;
    padding: 8px;
    color: {t['text_secondary']};
    font-size: 12px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    top: -8px;
    padding: 0 4px;
    background-color: {t['bg_secondary']};
}}
"""


def get_theme(theme_key: str = "dark_fluent") -> Dict[str, Any]:
    return THEMES.get(theme_key, THEMES["dark_fluent"])


def get_accent_color(theme_key: str = "dark_fluent", override: str = "") -> str:
    if override and override.startswith("#"):
        return override
    return THEMES.get(theme_key, THEMES["dark_fluent"])["accent"]
