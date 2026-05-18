import os
import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
from PyQt6.QtCore import Qt, QProcess, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QTextCursor, QColor

class TerminalPanel(QWidget):
    """A simple embedded terminal using QProcess."""
    
    def __init__(self, start_path: str = "", parent=None):
        super().__init__(parent)
        self.setFixedHeight(200)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.editor = QPlainTextEdit()
        self.editor.setReadOnly(False)
        self.editor.setFont(QFont("Cascadia Code", 10) if sys.platform == "win32" else QFont("Monospace", 10))
        self.editor.setObjectName("TerminalEditor")
        layout.addWidget(self.editor)
        
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._read_output)
        
        self.shell = "powershell.exe" if sys.platform == "win32" else "bash"
        self.process.setWorkingDirectory(start_path or os.path.expanduser("~"))
        self.process.start(self.shell)
        
        self.editor.installEventFilter(self)

    def apply_theme(self, bg: str, fg: str, accent: str):
        self.editor.setStyleSheet(f"""
            #TerminalEditor {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-top: 1px solid {accent};
                selection-background-color: {accent};
            }}
        """)

    def _read_output(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.editor.moveCursor(QTextCursor.MoveOperation.End)
        self.editor.insertPlainText(data)
        self.editor.moveCursor(QTextCursor.MoveOperation.End)

    def set_working_directory(self, path: str):
        if os.path.isdir(path):
            # In a real terminal we would send 'cd' command to the shell
            cmd = f"cd \"{path}\"\n" if sys.platform == "win32" else f"cd '{path}'\n"
            self.process.write(cmd.encode())

    def closeEvent(self, event):
        self._cleanup()
        super().closeEvent(event)

    def _cleanup(self):
        if hasattr(self, "process") and self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(500):
                self.process.kill()

    def __del__(self):
        self._cleanup()

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj is self.editor and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                cursor = self.editor.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.editor.setTextCursor(cursor)
                
                # Get the last line as command
                text = self.editor.toPlainText().splitlines()
                if text:
                    last_line = text[-1]
                    # This is naive as it includes the prompt. 
                    # For a better terminal we would need to track the prompt position.
                    # But for now, let's just send the last part.
                    # A better way is to capture key events and buffer them.
                    pass 
                
            # To keep it simple for this prototype, we'll just forward everything
            # but we need to prevent deleting the prompt etc.
            # Real terminal implementation is complex.
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        # Forward keys to process
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.process.write(b"\n")
        elif event.text():
            self.process.write(event.text().encode())
        super().keyPressEvent(event)
