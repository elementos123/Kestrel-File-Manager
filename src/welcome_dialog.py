"""First-run onboarding dialog — quick tour of the app's key features."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from src.i18n import t
from src.toggle_switch import ToggleSwitch
from src import icon_provider as ico

_CARDS = [
    ("dlg.welcome.card.spotlight.title", "dlg.welcome.card.spotlight.body", ico.bolt_icon),
    ("dlg.welcome.card.dual.title",      "dlg.welcome.card.dual.body",      ico.dual_panel_icon),
    ("dlg.welcome.card.terminal.title",  "dlg.welcome.card.terminal.body",  ico.terminal_icon),
    ("dlg.welcome.card.preview.title",   "dlg.welcome.card.preview.body",   ico.eye_icon),
]


def _mix(c: QColor, target: QColor, amount: float) -> QColor:
    r = round(c.red()   + (target.red()   - c.red())   * amount)
    g = round(c.green() + (target.green() - c.green()) * amount)
    b = round(c.blue()  + (target.blue()  - c.blue())  * amount)
    return QColor(r, g, b)


class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("dlg.welcome.title"))
        self.setFixedWidth(600)
        self.setModal(True)

        accent = ToggleSwitch._C_ON
        accent_dark = _mix(accent, QColor("#000000"), 0.35)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header banner ──────────────────────────────────
        banner = QFrame()
        banner.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 {accent.name()}, stop:1 {accent_dark.name()}); "
            f"border-top-left-radius: 8px; border-top-right-radius: 8px;"
        )
        banner_l = QVBoxLayout(banner)
        banner_l.setContentsMargins(28, 26, 28, 24)
        banner_l.setSpacing(6)

        badge = QLabel()
        badge.setPixmap(ico.rocket_icon("#ffffff").pixmap(24, 24))
        badge.setFixedSize(48, 48)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            "background: rgba(255,255,255,0.18); border-radius: 24px; border: none;"
        )
        banner_l.addWidget(badge)

        heading = QLabel(t("dlg.welcome.heading"))
        heading.setStyleSheet(
            "font-size: 21px; font-weight: 700; color: white; margin-top: 6px; "
            "background: transparent; border: none;"
        )
        heading.setWordWrap(True)
        banner_l.addWidget(heading)

        subtitle = QLabel(t("dlg.welcome.subtitle"))
        subtitle.setStyleSheet(
            "color: rgba(255,255,255,0.85); font-size: 12px; background: transparent; "
            "border: none; margin-left: 16px;"
        )
        subtitle.setWordWrap(True)
        banner_l.addWidget(subtitle)

        root.addWidget(banner)

        # ── Body ────────────────────────────────────────────
        body = QFrame()
        body.setStyleSheet("background: transparent;")
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(24, 20, 24, 18)
        body_l.setSpacing(16)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        for i, (title_key, body_key, icon) in enumerate(_CARDS):
            card = self._build_card(icon, t(title_key), t(body_key), accent)
            grid.addWidget(card, i // 2, i % 2)
        body_l.addLayout(grid)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("border: none; background: rgba(127,127,127,0.2);")
        sep.setFixedHeight(1)
        body_l.addWidget(sep)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        shortcuts_btn = QPushButton(t("dlg.welcome.view_shortcuts"))
        shortcuts_btn.setMinimumHeight(34)
        shortcuts_btn.clicked.connect(self._open_shortcuts)
        btn_row.addWidget(shortcuts_btn)
        btn_row.addStretch()
        start_btn = QPushButton(t("dlg.welcome.start"))
        start_btn.setObjectName("AccentButton")
        start_btn.setMinimumHeight(34)
        start_btn.setMinimumWidth(120)
        start_btn.clicked.connect(self.accept)
        start_btn.setDefault(True)
        btn_row.addWidget(start_btn)
        body_l.addLayout(btn_row)

        root.addWidget(body)

    @staticmethod
    def _build_card(icon_fn, title: str, body: str, accent: QColor) -> QFrame:
        card = QFrame()
        card.setStyleSheet("background: transparent; border: none;")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        card.setMinimumHeight(120)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(10)

        # Title row: no background box, just the icon badge + bold title.
        header = QHBoxLayout()
        header.setSpacing(10)

        icon_badge = QLabel()
        icon_badge.setPixmap(icon_fn(accent.name()).pixmap(16, 16))
        icon_badge.setFixedSize(36, 36)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setStyleSheet(
            f"border-radius: 18px; border: none; "
            f"background: rgba({accent.red()},{accent.green()},{accent.blue()},0.16);"
        )
        header.addWidget(icon_badge)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 13px; font-weight: 700; background: transparent; border: none;")
        title_lbl.setWordWrap(True)
        header.addWidget(title_lbl, 1)
        layout.addLayout(header)

        # Content: no fill, just a subtle outline with its own padding.
        body_box = QFrame()
        body_box.setStyleSheet(
            "background: transparent; border: 1px solid rgba(127,127,127,0.20); border-radius: 8px;"
        )
        body_l = QVBoxLayout(body_box)
        body_l.setContentsMargins(16, 14, 16, 14)

        body_lbl = QLabel(body)
        body_lbl.setWordWrap(True)
        body_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_lbl.setStyleSheet(
            "color: #999; font-size: 11px; line-height: 140%; background: transparent; border: none;"
        )
        body_l.addWidget(body_lbl)

        layout.addWidget(body_box, 1)

        return card

    def _open_shortcuts(self):
        from src.shortcuts_dialog import ShortcutsDialog
        ShortcutsDialog(self).exec()
