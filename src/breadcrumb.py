import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy,
    QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal


class BreadcrumbWidget(QWidget):
    navigate = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BreadcrumbWidget")
        self.setFixedHeight(36)

        self._outer = QHBoxLayout(self)
        self._outer.setContentsMargins(6, 0, 6, 0)
        self._outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setFixedHeight(36)

        inner_widget = QWidget()
        self._inner = QHBoxLayout(inner_widget)
        self._inner.setContentsMargins(4, 0, 4, 0)
        self._inner.setSpacing(0)
        self._inner.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        scroll.setWidget(inner_widget)
        self._outer.addWidget(scroll)

    def set_path(self, path: str):
        while self._inner.count():
            item = self._inner.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        parts = self._split_path(path)

        for i, (label, full_path) in enumerate(parts):
            btn = QPushButton(label)
            btn.setObjectName("BreadcrumbButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFlat(True)
            btn.setFixedHeight(28)
            btn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

            if i == len(parts) - 1:
                btn.setStyleSheet(
                    "font-weight: 600; color: white;"
                    "background: transparent; border: none;"
                    "padding: 3px 8px; border-radius: 4px;"
                )
            else:
                btn.setStyleSheet(
                    "background: transparent; border: none;"
                    "padding: 3px 8px; border-radius: 4px;"
                )

            navigate_path = full_path
            btn.clicked.connect(lambda _, p=navigate_path: self.navigate.emit(p))
            self._inner.addWidget(btn)

            if i < len(parts) - 1:
                sep = QLabel("›")
                sep.setStyleSheet("color: #555; font-size: 14px; padding: 0 2px;")
                sep.setFixedHeight(28)
                self._inner.addWidget(sep)

        self._inner.addStretch()

    @staticmethod
    def _split_path(path: str) -> list[tuple[str, str]]:
        path = os.path.normpath(path)
        parts = []
        current = path
        while True:
            parent = os.path.dirname(current)
            if parent == current:
                # Root
                parts.append((current, current))
                break
            name = os.path.basename(current)
            parts.append((name, current))
            current = parent
        parts.reverse()
        return parts
