import sqlite3
from pathlib import Path
from PyQt6.QtWidgets import QMessageBox, QPushButton, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from PyQt6.QtGui import QIcon

from config import DB_PATH, ICON_PATH, APP_NAME


class DatabaseConnection:
    """Handles SQLite database connection and validation."""
    
    def __init__(self, db_path=None):
        self.connection = None
        self.error_message = ""
        self.db_path = db_path or DB_PATH  # use config path if not specified
        
    def connect(self, db_path=None):
        """Connect to the database and validate."""
        if db_path:
            self.db_path = db_path
            
        try:
            if not Path(self.db_path).exists():
                self.error_message = f"Database file not found at:\n{self.db_path}"
                return False
                
            self.connection = sqlite3.connect(str(self.db_path))
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if not tables:
                self.error_message = "Database is empty (no tables found)"
                return False
                
            return True
            
        except sqlite3.Error as e:
            self.error_message = f"Database error:\n{str(e)}"
            return False
        except Exception as e:
            self.error_message = f"Unexpected error:\n{str(e)}"
            return False
    
    def get_table_names(self):
        if not self.connection:
            return []
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            return [row[0] for row in cursor.fetchall()]
        except:
            return []
    
    def get_table_data(self, table_name):
        if not self.connection:
            return [], []
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            cursor.execute(f"SELECT * FROM {table_name}")
            data = cursor.fetchall()
            return columns, data
        except sqlite3.Error as e:
            print(f"Error loading table {table_name}: {e}")
            return [], []
    
    def close(self):
        if self.connection:
            self.connection.close()


class StartupDialog(QDialog):
    """Custom startup dialog with three buttons."""
    
    def __init__(self, original_found, parent=None):
        super().__init__(parent)
        self.setWindowTitle(APP_NAME)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        
        layout = QVBoxLayout(self)
        
        # Main message
        msg_label = QLabel()
        if original_found:
            msg_label.setText("✅ Original Database Found!")
        else:
            msg_label.setText("❌ Original Database not found.")
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)
        
        # Path info
        path_label = QLabel(f"Location: {DB_PATH}")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        # Warning if original not found
        if not original_found:
            warning = QLabel("⚠️ If you choose another database, simulation may not work correctly.")
            warning.setWordWrap(True)
            warning.setStyleSheet("color: orange; font-weight: bold;")
            layout.addWidget(warning)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.run_btn = QPushButton("🚀 Run!")
        self.run_btn.setEnabled(original_found)
        self.run_btn.clicked.connect(lambda: self.done(1))
        btn_layout.addWidget(self.run_btn)
        
        self.choose_btn = QPushButton("📂 Choose another Database")
        self.choose_btn.clicked.connect(lambda: self.done(2))
        btn_layout.addWidget(self.choose_btn)
        
        self.exit_btn = QPushButton("❌ EXIT")
        self.exit_btn.clicked.connect(lambda: self.done(3))
        btn_layout.addWidget(self.exit_btn)
        
        layout.addLayout(btn_layout)


def show_startup_dialog(parent, db_connected, error_msg=""):
    """Show startup dialog and return (action, db_path)."""
    dialog = StartupDialog(db_connected, parent)
    result = dialog.exec()
    
    if result == 1:  # Run with original
        return ("run", None)
    elif result == 2:  # Choose another
        # Warning gies first
        warning_box = QMessageBox()
        warning_box.setIcon(QMessageBox.Icon.Warning)
        warning_box.setWindowTitle("⚠️ WARNING")
        warning_box.setText(
            "<h3>You have selected a non-original database.</h3>"
            "<p>The program may not function correctly, and simulation may fail.</p>"
            "<p>Before proceeding with any operations, please use:</p>"
            "<p><b>Main Menu → Database → Check Database</b></p>"
        )
        warning_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        warning_box.setDefaultButton(QMessageBox.StandardButton.Ok)
        
        proceed_button = warning_box.button(QMessageBox.StandardButton.Ok)
        proceed_button.setText("PROCEED")
        
        warning_box.exec()
        
        # After warning open file directory dialogue
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            "Select Database File",
            str(DB_PATH.parent),
            "SQLite Database (*.db *.sqlite);;All Files (*)"
        )
        if file_path:
            return ("choose", file_path)
        else:
            return ("exit", None)