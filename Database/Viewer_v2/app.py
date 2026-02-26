import sys
import datetime
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon

from config import APP_NAME, ICON_PATH, LOGS_PATH, DB_PATH
from core.database import DatabaseConnection
from core.startup_dialog import show_startup_dialog  #  it works now
from styles.stylesheets import get_main_stylesheet


def write_to_log():
    """Write application start to log file"""
    try:
        with open(LOGS_PATH, 'a', encoding='utf-8') as f:
            now = datetime.datetime.now()
            f.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - Database Viewer started\n")
    except Exception as e:
        print(f"Failed to write to log: {e}")


def setup_database_connection(target_db_path):
    """Setup and test database connection"""
    db = DatabaseConnection(target_db_path)
    if not db.connect():
        QMessageBox.critical(
            None, 
            "Error", 
            f"Failed to connect to database:\n{db.error_message}"
        )
        sys.exit(1)
    return db


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    if Path(ICON_PATH).exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    app.setStyleSheet(get_main_stylesheet())

    # Try connecting to original DB
    original_db = DatabaseConnection()
    db_connected = original_db.connect()
    error_message = original_db.error_message if not db_connected else ""

    # Show startup dialog - now it exists in core.startup_dialog
    action, chosen_path = show_startup_dialog(None, db_connected, error_message)

    if action == "exit":
        sys.exit(0)

    # Determine target database
    target_db = DB_PATH if action == "continue" else chosen_path

    # Close original connection if it was opened
    try:
        original_db.close()
    except Exception:
        pass

    # Setup final database connection
    db = setup_database_connection(target_db)
    write_to_log()

    # Start main window
    from ui.main_window import MainWindow
    window = MainWindow(db)
    window.show()

    exit_code = app.exec()
    db.close()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())