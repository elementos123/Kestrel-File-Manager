import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from src import icon_provider as ico

class TransferItem(QFrame):
    """A single row in the transfer manager showing progress for one operation."""
    cancelled = pyqtSignal()

    def __init__(self, op_type: str, count: int, destination: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            TransferItem {
                background: #252526;
                border: 1px solid #333;
                border-radius: 6px;
                margin: 2px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        
        # Header: Icon + Op Type + Count
        header = QHBoxLayout()
        icon = QLabel("📋" if op_type == "copy" else "📦")
        title = QLabel(f"{'Copiando' if op_type == 'copy' else 'Moviendo'} {count} elemento(s)")
        title.setStyleSheet("font-weight: bold; font-size: 11px;")
        
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setFixedSize(18, 18)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; color: #666; font-weight: bold; }
            QPushButton:hover { color: #f44747; }
        """)
        self.cancel_btn.clicked.connect(self.cancelled.emit)
        
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.cancel_btn)
        layout.addLayout(header)
        
        # Current file / Status
        self.status_lbl = QLabel("Preparando...")
        self.status_lbl.setStyleSheet("color: #888; font-size: 10px;")
        self.status_lbl.setWordWrap(False)
        layout.addWidget(self.status_lbl)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setStyleSheet("""
            QProgressBar { background: #1e1e1e; border: none; border-radius: 2px; }
            QProgressBar::chunk { background: #0078d4; border-radius: 2px; }
        """)
        layout.addWidget(self.progress)
        
        # Dest info
        dest_lbl = QLabel(f"Hacia: {os.path.basename(destination) or destination}")
        dest_lbl.setStyleSheet("color: #555; font-size: 9px;")
        layout.addWidget(dest_lbl)

    def update_progress(self, value: int, current_file: str):
        self.progress.setValue(value)
        self.status_lbl.setText(current_file)

class TransferManager(QWidget):
    """Container for active and finished file transfers."""
    all_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setMinimumHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Title bar
        header = QFrame()
        header.setFixedHeight(30)
        header.setStyleSheet("background: #1e1e1e; border-top: 1px solid #333;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(10, 0, 10, 0)
        
        title = QLabel("TRANSFERENCIAS")
        title.setStyleSheet("font-size: 10px; font-weight: bold; color: #666; letter-spacing: 1px;")
        hl.addWidget(title)
        hl.addStretch()
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("background: transparent; border: none; color: #666;")
        self.close_btn.clicked.connect(lambda: self.setVisible(False))
        hl.addWidget(self.close_btn)
        
        layout.addWidget(header)
        
        # Scroll area for items
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: #1e1e1e;")
        
        self.container = QWidget()
        self.items_layout = QVBoxLayout(self.container)
        self.items_layout.setContentsMargins(4, 4, 4, 4)
        self.items_layout.setSpacing(2)
        self.items_layout.addStretch()
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        
        self._transfers = {} # worker -> item

    def add_transfer(self, worker):
        item = TransferItem(worker.operation, len(worker.sources), worker.destination)
        # Insert at top (index 0) but before the final stretch
        self.items_layout.insertWidget(0, item)
        self._transfers[worker] = item
        
        worker.progress.connect(item.update_progress)
        worker.finished.connect(lambda ok, msg, w=worker: self._on_transfer_finished(w, ok, msg))
        item.cancelled.connect(worker.cancel)
        
        self.setVisible(True)

    def _on_transfer_finished(self, worker, ok: bool, msg: str):
        item = self._transfers.get(worker)
        if not item:
            return
            
        if ok:
            item.status_lbl.setText("Completado")
            item.progress.setValue(100)
            item.progress.setStyleSheet("QProgressBar::chunk { background: #4ec9b0; }")
        else:
            item.status_lbl.setText(f"Error: {msg}" if msg else "Cancelado")
            item.progress.setStyleSheet("QProgressBar::chunk { background: #f44747; }")
        
        # Change cancel button to a clear button
        item.cancel_btn.setText("✕")
        item.cancel_btn.setToolTip("Quitar de la lista")
        try:
            item.cancel_btn.clicked.disconnect()
        except TypeError:
            pass
        item.cancel_btn.clicked.connect(lambda: self._remove_transfer(worker))
        
        # Check if all ACTIVE transfers are done
        active = [w for w in self._transfers.keys() if w.isRunning()]
        if not active:
            self.all_finished.emit()

    def _remove_transfer(self, worker):
        item = self._transfers.pop(worker, None)
        if item:
            item.deleteLater()
            # If the list is now empty, we can hide the panel
            if not self._transfers:
                self.setVisible(False)
