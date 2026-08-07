import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QScrollArea, QFrame, QToolButton,
    QGraphicsDropShadowEffect, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor
from src import icon_provider as ico
from src.toggle_switch import ToggleSwitch
from src.i18n import t

_STATE_COLORS = {
    "active": None,   # resolved from the live accent at build time
    "done":   "#4ec9b0",
    "warn":   "#d19a66",
    "error":  "#e06c75",
}


def _bar_css(color: str) -> str:
    return (
        "QProgressBar { background: rgba(127,127,127,0.15); border: none; border-radius: 3px; }"
        f"QProgressBar::chunk {{ background: {color}; border-radius: 3px; }}"
    )


class TransferItem(QFrame):
    """A single card in the transfer panel showing progress for one operation."""
    cancelled = pyqtSignal()
    pause_toggled = pyqtSignal()

    def __init__(self, op_type: str, count: int, destination: str, parent=None):
        super().__init__(parent)
        self._error_count = 0
        self._finished = False
        self._accent = ToggleSwitch._C_ON.name()

        self.setStyleSheet(
            "TransferItem { background: rgba(127,127,127,0.05); "
            "border: 1px solid rgba(127,127,127,0.14); border-radius: 10px; }"
        )
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        body = QWidget()
        body.setStyleSheet("background: transparent; border: none;")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(12, 11, 12, 11)
        layout.setSpacing(8)
        outer.addWidget(body)

        # ── Header: badge + title/subtitle + actions ──────
        header = QHBoxLayout()
        header.setSpacing(10)

        self._badge = QLabel()
        self._badge.setFixedSize(30, 30)
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setStyleSheet(self._badge_css(self._accent))
        self._badge.setPixmap(
            (ico.copy_icon(self._accent) if op_type == "copy" else ico.move_icon(self._accent)).pixmap(15, 15)
        )
        header.addWidget(self._badge)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title_key = "transfer.copying" if op_type == "copy" else "transfer.moving"
        self._title_lbl = QLabel(t(title_key, count=count))
        self._title_lbl.setStyleSheet(
            "font-weight: 700; font-size: 12px; background: transparent; border: none;"
        )
        self._title_lbl.setWordWrap(False)
        dest_lbl = QLabel(t("transfer.to", name=os.path.basename(destination) or destination))
        dest_lbl.setStyleSheet("color: #888; font-size: 10px; background: transparent; border: none;")
        dest_lbl.setWordWrap(False)
        title_col.addWidget(self._title_lbl)
        title_col.addWidget(dest_lbl)
        header.addLayout(title_col, 1)

        actions = QHBoxLayout()
        actions.setSpacing(2)
        self.pause_btn = self._round_button(ico.pause_icon, t("transfer.pause"), hover="rgba(255,255,255,0.10)")
        self.pause_btn.clicked.connect(self.pause_toggled.emit)
        self.cancel_btn = self._round_button(ico.close_icon, t("transfer.cancel"), hover="rgba(224,108,117,0.18)")
        self.cancel_btn.clicked.connect(self.cancelled.emit)
        actions.addWidget(self.pause_btn)
        actions.addWidget(self.cancel_btn)
        header.addLayout(actions)

        layout.addLayout(header)

        # ── Progress row: bar + percent ────────────────────
        prog_row = QHBoxLayout()
        prog_row.setSpacing(8)
        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet(_bar_css(self._accent))
        self._pct_lbl = QLabel("0%")
        self._pct_lbl.setStyleSheet(
            "color: #aaa; font-size: 10px; font-weight: 600; background: transparent; border: none;"
        )
        self._pct_lbl.setFixedWidth(30)
        self._pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        prog_row.addWidget(self.progress, 1)
        prog_row.addWidget(self._pct_lbl)
        layout.addLayout(prog_row)

        # ── Status line ─────────────────────────────────────
        self.status_lbl = QLabel(t("op.preparing"))
        self.status_lbl.setStyleSheet("color: #999; font-size: 10px; background: transparent; border: none;")
        fm = self.status_lbl.fontMetrics()
        self.status_lbl.setMinimumHeight(fm.height())
        layout.addWidget(self.status_lbl)

    @staticmethod
    def _badge_css(color: str) -> str:
        c = QColor(color)
        return (
            f"border-radius: 15px; background: rgba({c.red()},{c.green()},{c.blue()},0.16); "
            f"border: none;"
        )

    @staticmethod
    def _round_button(icon_fn, tooltip: str, hover: str) -> QToolButton:
        btn = QToolButton()
        btn.setIcon(icon_fn("#999"))
        btn.setIconSize(QSize(13, 13))
        btn.setFixedSize(24, 24)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setStyleSheet(
            "QToolButton { background: transparent; border: none; border-radius: 12px; }"
            f"QToolButton:hover {{ background: {hover}; }}"
        )
        return btn

    def _elide(self, label: QLabel, text: str):
        fm = label.fontMetrics()
        label.setText(fm.elidedText(text, Qt.TextElideMode.ElideMiddle, max(label.width(), 160)))
        label.setToolTip(text)

    def update_progress(self, value: int, current_file: str, index: int, total: int):
        self.progress.setValue(value)
        self._pct_lbl.setText(f"{value}%")
        suffix = f"   {t('op.of_total', index=index, total=total)}" if total > 1 else ""
        self._elide(self.status_lbl, f"{current_file}{suffix}")

    def note_error(self, path: str, message: str):
        self._error_count += 1

    def set_paused_visual(self, paused: bool):
        self.pause_btn.setIcon(ico.play_icon("#999") if paused else ico.pause_icon("#999"))
        self.pause_btn.setToolTip(t("transfer.resume") if paused else t("transfer.pause"))
        if paused:
            self.status_lbl.setText(t("op.paused"))

    def mark_finished(self, ok: bool, msg: str):
        self._finished = True
        self.pause_btn.setVisible(False)

        if ok and not self._error_count:
            state, text = "done", t("op.completed")
            self.progress.setValue(100)
            self._pct_lbl.setText("100%")
        elif ok and self._error_count:
            state, text = "warn", msg or t("op.completed_with_errors", done="?", failed=self._error_count)
        else:
            state, text = "error", msg or t("op.cancelled")

        color = _STATE_COLORS[state] or self._accent
        self.progress.setStyleSheet(_bar_css(color))
        self._badge.setStyleSheet(self._badge_css(color))
        self._badge.setPixmap((ico.check_icon(color) if state == "done" else ico.error_icon(color)).pixmap(15, 15))
        self._elide(self.status_lbl, text)

        self.cancel_btn.setIcon(ico.close_icon("#999"))
        self.cancel_btn.setToolTip(t("transfer.dismiss"))
        try:
            self.cancel_btn.clicked.disconnect()
        except TypeError:
            pass
        return self.cancel_btn


class TransferManager(QFrame):
    """Floating, dismissible panel listing active and finished file transfers."""
    all_finished = pyqtSignal()
    count_changed = pyqtSignal(int, int)  # active, total

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TransferManager")
        self.setMinimumWidth(300)
        self.setMaximumWidth(380)
        self.setMinimumHeight(140)
        self.setStyleSheet("""
            #TransferManager {
                background: #1c1c1e;
                border: 1px solid rgba(127,127,127,0.22);
                border-radius: 12px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(42)
        shadow.setXOffset(0)
        shadow.setYOffset(12)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Title bar ───────────────────────────────────────
        header = QFrame()
        header.setFixedHeight(46)
        header.setStyleSheet(
            "background: transparent; border: none; "
            "border-bottom: 1px solid rgba(127,127,127,0.16);"
        )
        hl = QHBoxLayout(header)
        hl.setContentsMargins(14, 0, 10, 0)
        hl.setSpacing(4)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title = QLabel(t("transfer.panel_title"))
        title.setStyleSheet(
            "font-size: 12px; font-weight: 700; background: transparent; border: none;"
        )
        self._summary_lbl = QLabel(t("transfer.empty"))
        self._summary_lbl.setStyleSheet(
            "font-size: 10px; color: #888; background: transparent; border: none;"
        )
        title_col.addWidget(title)
        title_col.addWidget(self._summary_lbl)
        hl.addLayout(title_col)
        hl.addStretch()

        self.clear_btn = QToolButton()
        self.clear_btn.setIcon(ico.clear_icon("#888"))
        self.clear_btn.setIconSize(QSize(14, 14))
        self.clear_btn.setFixedSize(26, 26)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setToolTip(t("transfer.clear_completed"))
        self.clear_btn.setStyleSheet("""
            QToolButton { background: transparent; border: none; border-radius: 13px; }
            QToolButton:hover:!disabled { background: rgba(255,255,255,0.08); }
        """)
        self.clear_btn.clicked.connect(self.clear_completed)
        hl.addWidget(self.clear_btn)

        self.close_btn = QToolButton()
        self.close_btn.setIcon(ico.close_icon("#888"))
        self.close_btn.setIconSize(QSize(14, 14))
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setToolTip(t("transfer.hide_panel"))
        self.close_btn.setStyleSheet("""
            QToolButton { background: transparent; border: none; border-radius: 13px; }
            QToolButton:hover { background: rgba(255,255,255,0.08); }
        """)
        self.close_btn.clicked.connect(lambda: self.setVisible(False))
        hl.addWidget(self.close_btn)

        layout.addWidget(header)

        # ── Scroll area for items ───────────────────────────
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.items_layout = QVBoxLayout(self.container)
        self.items_layout.setContentsMargins(8, 8, 8, 8)
        self.items_layout.setSpacing(6)
        self.items_layout.addStretch()

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.empty_lbl = QLabel(t("transfer.empty"))
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_lbl.setStyleSheet(
            "color: #666; font-size: 11px; padding: 28px 16px; background: transparent; border: none;"
        )
        layout.addWidget(self.empty_lbl)

        self._transfers = {}  # worker -> item
        self._update_empty_state()

    # ── Public API ──────────────────────────────────────────

    def toggle(self):
        self.setVisible(not self.isVisible())
        if self.isVisible():
            self.raise_()

    def active_count(self) -> int:
        return sum(1 for w in self._transfers if w.isRunning())

    def content_height_hint(self) -> int:
        """Natural height for the current content, for the parent to clamp."""
        header_h = 46
        if not self._transfers:
            return header_h + self.empty_lbl.sizeHint().height()
        items_h = self.container.sizeHint().height()
        return header_h + items_h

    def add_transfer(self, worker):
        item = TransferItem(worker.operation, len(worker.sources), worker.destination)
        self.items_layout.insertWidget(0, item)
        self._transfers[worker] = item

        worker.progress.connect(item.update_progress)
        worker.item_error.connect(item.note_error)
        worker.paused_changed.connect(item.set_paused_visual)
        worker.finished.connect(lambda ok, msg, w=worker: self._on_transfer_finished(w, ok, msg))
        item.cancelled.connect(worker.cancel)
        item.pause_toggled.connect(worker.toggle_pause)

        self.setVisible(True)
        self.raise_()
        self._update_empty_state()
        self._emit_count()

    def clear_completed(self):
        for worker in [w for w in self._transfers if not w.isRunning()]:
            self._remove_transfer(worker)

    # ── Internals ───────────────────────────────────────────

    def _on_transfer_finished(self, worker, ok: bool, msg: str):
        item = self._transfers.get(worker)
        if not item:
            return
        cancel_btn = item.mark_finished(ok, msg)
        cancel_btn.clicked.connect(lambda: self._remove_transfer(worker))
        self._emit_count()

        if self.active_count() == 0:
            self.all_finished.emit()

    def _remove_transfer(self, worker):
        item = self._transfers.pop(worker, None)
        if item:
            item.deleteLater()
        self._update_empty_state()
        self._emit_count()

    def _update_empty_state(self):
        has_items = bool(self._transfers)
        self.scroll.setVisible(has_items)
        self.empty_lbl.setVisible(not has_items)
        self.clear_btn.setEnabled(any(not w.isRunning() for w in self._transfers))

    def _emit_count(self):
        active = self.active_count()
        total = len(self._transfers)
        if total == 0:
            self._summary_lbl.setText(t("transfer.empty"))
        elif active == 0:
            self._summary_lbl.setText(t("transfer.all_done", total=total))
        else:
            self._summary_lbl.setText(t("transfer.active_of_total", active=active, total=total))
        self.count_changed.emit(active, total)
