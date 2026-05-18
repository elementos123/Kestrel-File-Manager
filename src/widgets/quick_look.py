import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPlainTextEdit, QScrollArea
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QFont

from src.utils import is_image, is_text, read_text_preview

class QuickLookDialog(QDialog):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Vista rápida: {os.path.basename(path)}")
        self.resize(800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if is_image(path):
            lbl = QLabel()
            pix = QPixmap(path)
            if not pix.isNull():
                lbl.setPixmap(pix.scaled(780, 580, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)
        elif is_text(path):
            text = read_text_preview(path, max_bytes=65536)
            edit = QPlainTextEdit()
            edit.setReadOnly(True)
            edit.setPlainText(text or "(Sin contenido o error de lectura)")
            edit.setFont(QFont("Cascadia Code", 10))
            layout.addWidget(edit)
        else:
            lbl = QLabel(f"Sin previsualización disponible para:\n{os.path.basename(path)}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl)
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.close()
        super().keyPressEvent(event)
