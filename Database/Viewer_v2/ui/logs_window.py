"""
Logs viewer window.
Displays contents of Logs.txt in a read-only text area.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtCore import Qt
from config import LOGS_PATH


class LogsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Viewer Logs")
        self.setGeometry(300, 300, 600, 400)
        self.setMinimumSize(500, 300)

        layout = QVBoxLayout(self)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFontFamily("Courier New")
        layout.addWidget(self.text_area)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.load_logs()

    def load_logs(self):
        """Read Logs.txt and display content."""
        try:
            with open(LOGS_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_area.setPlainText(content if content else "Log file is empty.")
        except FileNotFoundError:
            self.text_area.setPlainText("Log file not found.")
        except Exception as e:
            self.text_area.setPlainText(f"Error reading log file: {e}")