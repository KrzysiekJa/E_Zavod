import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

from config import APP_NAME, ICON_PATH, DB_PATH


class StartupDialog(QDialog):
    def __init__(self, db_connected, error_msg="", parent=None):
        super().__init__(parent)
        self.db_connected = db_connected
        self.error_msg = error_msg
        self.chosen_path = None
        self.action = None

        self.setWindowTitle(APP_NAME)
        self.setFixedSize(550, 450)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        if Path(ICON_PATH).exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        self._setup_ui()
        self._connect_buttons()

    def _setup_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        self._add_status_icon(layout)
        self._add_title(layout)
        
        if not self.db_connected:
            self._add_database_not_found_section(layout)
        
        self._add_separator(layout)
        self._add_buttons(layout)

    def _add_status_icon(self, layout):
        """Add status icon based on DB connection"""
        status_icon = QLabel()
        status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.db_connected:
            status_icon.setText("✅")
            status_icon.setStyleSheet("font-size: 72px; color: #4CAF50;")
        else:
            status_icon.setText("❌")
            status_icon.setStyleSheet("font-size: 72px; color: #f44336;")
        
        layout.addWidget(status_icon)

    def _add_title(self, layout):
        """Add title based on DB connection"""
        title = QLabel()
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        
        if self.db_connected:
            title.setText(f"Original Database Found ({Path(DB_PATH).name})")
            title.setStyleSheet("color: #4CAF50;")
        else:
            title.setText("Database Not Found")
            title.setStyleSheet("color: #ff0000;")
        
        layout.addWidget(title)

    def _add_database_not_found_section(self, layout):
        """Add section for when database is not found"""
        looking_text = QLabel(
            "<b>Looking for</b><br>"
            f"<span style='font-size: 16pt; font-weight: bold; color: #7e008c;'>{Path(DB_PATH).name}</span><br>"
            "<i>(type: SQLite)</i>"
        )
        looking_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        looking_text.setWordWrap(True)
        looking_text.setStyleSheet("padding: 10px;") 
        layout.addWidget(looking_text)



        # Required location text 
        required_location = QLabel(
            f"<b>Required {Path(DB_PATH).name} file location:</b><br>"
            f"{Path(DB_PATH).parent.resolve()}"
        )
        required_location.setAlignment(Qt.AlignmentFlag.AlignCenter)
        required_location.setWordWrap(True)
        required_location.setStyleSheet("""
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12pt;
            margin-top: 5px;
        """)
        layout.addWidget(required_location)

        # Warning block 
        warning_label = QLabel(
            "⚠️ <b>WARNING</b> ⚠️<br><br>"
            "Using a non-original database may cause:<br>"
            "• Simulator malfunction<br>"
            "• Incorrect calculations<br>"
            "• Unexpected behavior<br><br>"
            "<i>Use at your own risk!</i>"
        )
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("""
            color: #ff0000;
            background-color: #f5dfdf;
            border: 2px solid #ff8c00;
            border-radius: 5px;
            padding: 15px;
            font-size: 14pt;
            margin-top: 10px;
        """) 
        layout.addWidget(warning_label)

    def _add_separator(self, layout):
        """Add separator line"""
        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #cccccc; margin: 10px 0;")
        layout.addWidget(separator)

    def _add_buttons(self, layout):
        """Add action buttons"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        if self.db_connected:
            self.run_btn = self._create_button(
                "🚀 RUN", "#4CAF50", "#45a049", "#3d8b40", 150
            )
            self.run_btn.clicked.connect(self.accept_original)
            button_layout.addWidget(self.run_btn)

        self.choose_btn = self._create_button(
            "📂 CHOOSE DATABASE", "#2196F3", "#1976D2", "#0d47a1", 180
        )
        self.choose_btn.clicked.connect(self.choose_database)
        button_layout.addWidget(self.choose_btn)

        self.exit_btn = self._create_button(
            "❌ EXIT", "#f44336", "#d32f2f", "#b71c1c", 120
        )
        self.exit_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.exit_btn)

        layout.addLayout(button_layout)

    def _create_button(self, text, color, hover_color, pressed_color, width):
        """Helper method to create styled buttons"""
        btn = QPushButton(text)
        btn.setFixedSize(width, 50)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }}
            QPushButton:hover {{ background-color: {hover_color}; }}
            QPushButton:pressed {{ background-color: {pressed_color}; }}
        """)
        return btn

    def _connect_buttons(self):
        """Connect button signals"""
        pass

    def accept_original(self):
        """Continue with original DB"""
        self.action = "continue"
        self.accept()

    def choose_database(self):
        """Show warning and file dialog"""
        if self._show_warning_dialog():
            file_path = self._get_database_file()
            if file_path:
                self.chosen_path = file_path
                self.action = "choose"
                self.accept()

    def _show_warning_dialog(self):
        """Show warning dialog and return True if user proceeds"""
        warning_dialog = QDialog(self)
        warning_dialog.setWindowTitle("⚠️ WARNING")
        warning_dialog.setFixedSize(450, 300)
        warning_dialog.setModal(True)

        layout = QVBoxLayout(warning_dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        icon = QLabel("⚠️")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon)

        warning_text = QLabel(
            "<b>WARNING:</b> You are using a non-original database!<br><br>"
            "The simulator may not function correctly.<br>"
            "Use at your own risk."
        )
        warning_text.setWordWrap(True)
        warning_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_text.setStyleSheet("font-size: 12pt; color: #333333;")
        layout.addWidget(warning_text)

        info_text = QLabel(
            "<b>Check database accountability</b><br><br>"
            "Check database accountability using:<br>"
            "<b>Main Menu → Database → Check accountability of the database</b>"
        )
        info_text.setWordWrap(True)
        info_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_text.setStyleSheet("""
            font-size: 11pt;
            color: #333333;
            background-color: #ffffff;
            padding: 8px;
            border-radius: 4px;
        """)
        info_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(info_text)
        # instructions

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        proceed_btn = self._create_warning_button(
            "🚀 PROCEED", "#FFA500", "#FF8C00", 150
        )
        proceed_btn.clicked.connect(warning_dialog.accept)
        btn_layout.addWidget(proceed_btn)

        return_btn = self._create_warning_button(
            "🔙 RETURN", "#540350", "#5a6268", 150
        )
        return_btn.clicked.connect(warning_dialog.reject)
        btn_layout.addWidget(return_btn)

        layout.addLayout(btn_layout)

        return warning_dialog.exec() == QDialog.DialogCode.Accepted


    def _create_warning_button(self, text, color, hover_color, width):
        """Helper for warning dialog buttons"""
        btn = QPushButton(text)
        btn.setFixedSize(width, 40)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                font-size: 12pt;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """)
        return btn

    def _get_database_file(self):
        """Open file dialog and return selected path"""
        start_dir = str(Path(DB_PATH).parent)
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Database File",
            start_dir,
            "SQLite Database (*.db *.sqlite);;All Files (*)"
        )
        return file_path if file_path else None


def show_startup_dialog(parent, db_connected, error_msg=""):
    """
    Show startup dialog and return (action, chosen_path)
    action can be: "continue", "choose", "exit"
    """
    dialog = StartupDialog(db_connected, error_msg, parent)
    result = dialog.exec()
    
    if result == QDialog.DialogCode.Accepted:
        if dialog.action == "continue":
            return "continue", None
        elif dialog.action == "choose":
            return "choose", dialog.chosen_path
    
    return "exit", None