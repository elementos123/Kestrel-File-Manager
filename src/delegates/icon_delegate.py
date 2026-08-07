from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionViewItem
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QPainter, QColor, QPen

from src.toggle_switch import ToggleSwitch
from src.logger import get_logger

_log = get_logger("icon_delegate")


class IconDelegate(QStyledItemDelegate):
    """Draws a subtle rounded-rect selection highlight in icon mode."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        # paint() is a Qt virtual override with no return value C++ can
        # sanity-check — an uncaught exception here crashes the whole
        # process with an opaque "sipBadCatcherResult" error rather than a
        # normal traceback, so fall back to the default item painting
        # instead of raising through this boundary.
        try:
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            is_selected = bool(option.state & QStyle.StateFlag.State_Selected)
            is_hovered  = bool(option.state & QStyle.StateFlag.State_MouseOver)

            if is_selected:
                accent = ToggleSwitch._C_ON
                painter.setBrush(QColor(accent.red(), accent.green(), accent.blue(), 46))
                painter.setPen(QPen(accent, 1))
                painter.drawRoundedRect(option.rect.adjusted(2, 2, -2, -2), 6, 6)
            elif is_hovered:
                painter.setBrush(QColor("#2a2d2e"))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(option.rect.adjusted(2, 2, -2, -2), 6, 6)

            painter.restore()
            # Draw icon + text without the default selection background
            opt = QStyleOptionViewItem(option)
            opt.state &= ~QStyle.StateFlag.State_Selected
            opt.state &= ~QStyle.StateFlag.State_HasFocus
            super().paint(painter, opt, index)
        except Exception:
            _log.exception("IconDelegate.paint failed")
            try:
                painter.restore()
            except Exception:
                pass
            super().paint(painter, option, index)
