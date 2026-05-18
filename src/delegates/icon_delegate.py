from PyQt6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionViewItem
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QPainter, QColor, QPen

class IconDelegate(QStyledItemDelegate):
    """Draws a subtle rounded-rect selection highlight in icon mode."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)
        is_hovered  = bool(option.state & QStyle.StateFlag.State_MouseOver)

        if is_selected:
            painter.setBrush(QColor("#094771"))
            painter.setPen(QPen(QColor("#1a7bc4"), 1))
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
