from PyQt6.QtCore import QObject
from .grid_controller import GridController
from .highlight_controller import HighlightController
from .filter_controller import FilterController
from ui.search_controller import SearchController
from PyQt6.QtWidgets import QSplitter
import sys
import subprocess
import config
import traceback
from PyQt6.QtCore import QTimer
from debug_helper import debug

def global_exception_handler(exctype, value, tb):
    print("🔴 GLOBAL EXCEPTION HANDLER")
    print(f"Type: {exctype}")
    print(f"Value: {value}")
    print("Traceback:")
    traceback.print_tb(tb)
        
    # Global signal
    sys.excepthook = global_exception_handler


class BaseController(QObject):
    """Combines all controllers and connects them to the side menu."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.filter_controllers = {}  # table_name -> FilterController

        #  initialize sub-controllers (ONCE)
        self.grid = GridController(main_window)
        self.highlight = HighlightController()
        
        # Search controller
        self.search_controller = SearchController(main_window, main_window.side_menu)

        # connecting side_menu
        self._connect_side_menu()

        # connecting table signals
        self._connect_tables()

        # set to OFF when changing tabs
        self.main_window.tab_widget.currentChanged.connect(self._on_tab_changed)

        self.main_window.side_menu.freeze_rows_toggled.connect(self._on_freeze_toggled)

        # set signals for filter options in side_menu
        sm = main_window.side_menu
        sm.filter_exact_toggled.connect(self._on_filter_exact_toggled)
        sm.filter_case_toggled.connect(self._on_filter_case_toggled)

        # create settings manager
        from core.settings_manager import SettingsManager
        self.settings = SettingsManager()
        
        #register main window for settings
        self.settings.register_window(main_window)


        if hasattr(self.main_window.side_menu, 'find_db'):
            self.main_window.side_menu.find_db.clicked.connect(self.on_find_database)
        if hasattr(self.main_window.side_menu, 'exit_app'):
            self.main_window.side_menu.exit_app.clicked.connect(self.on_exit)


        from PyQt6.QtCore import qInstallMessageHandler
        def qt_message_handler(mode, context, message):
            print(f"🔴 Qt message: {message}")
            if "QScrollArea" in message or "deleted" in message:
                print("🔴🔴🔴 CRITICAL: Scroll area error detected!")
                import traceback
                traceback.print_stack()
        
            qInstallMessageHandler(qt_message_handler)

    def _on_freeze_toggled(self, enabled):
        for table in self._all_tables():
            table.set_freeze_enabled(enabled)
        self.main_window.status_bar.showMessage(f"Freeze rows: {'ON' if enabled else 'OFF'}")

    def _connect_side_menu(self):
        sm = self.main_window.side_menu
        #check if it is not destroyed
        try:
            sm.objectName()
        except RuntimeError:
            return
        
        sm.grid_toggled.connect(self.grid.set_enabled)
        sm.highlight_toggled.connect(self._on_highlight_toggled)

    def _connect_tables(self):
        for table in self._all_tables():
            table.cell_highlight_requested.connect(self._on_cell_clicked)
            table.set_highlight_enabled(self.highlight.enabled)

    def connect_table_signals(self):
        self._connect_tables()

    def _all_tables(self):
        return list(self.main_window.table_widgets.values())

    def _on_highlight_toggled(self, enabled):
        self.highlight.set_enabled(enabled)
        for table in self._all_tables():
            table.set_highlight_enabled(enabled)
            if hasattr(table, 'restore_search_highlight'):
                table.restore_search_highlight()  # Refresh search
        if not enabled:
            self.highlight.clear_all(self._all_tables())

    def _on_cell_clicked(self, row, col):
        if self.highlight.enabled:
            table = self._get_current_table()
            if table:
                self.highlight.highlight(table, row, col)

    def _get_current_table(self):
        index = self.main_window.tab_widget.currentIndex()
        if index >= 0:
            name = self.main_window.tab_widget.tabText(index)
            return self.main_window.table_widgets.get(name)
        return None

    def _on_tab_changed(self, index):
        """Handle tab change - reset filter options."""
        try:
            self.main_window.side_menu.filter_exact_cb.setChecked(False)
            self.main_window.side_menu.filter_case_cb.setChecked(False)
        except (AttributeError, RuntimeError):
            # Ignore errors
            pass
    # ============== buttons ==============
    def on_edit_database(self):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("Edit Database")
        msg.setText("NOT IMPLEMENTED YET")
        msg.setInformativeText("This module will be available in future versions.")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def on_print_report(self):
        """Print Report button - Launch DB_REPORT.py with current database."""
        import subprocess
        import sys
        from config import DATABASE_DIR, DB_PATH
        
        report_path = DATABASE_DIR / "DB_REPORT.py"
        if not report_path.exists():
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(f"Report module not found:\n{report_path}")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
            return
        
        if not self.main_window.db or not self.main_window.db.connection:
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("No database connection!")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()
            return
        
        current_db_path = str(DB_PATH)
        
        try:
            subprocess.Popen([sys.executable, str(report_path), current_db_path])
            self.main_window.status_bar.showMessage("Report module launched")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(f"Failed to launch report module:\n{str(e)}")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.exec()

    def on_additional_window(self):
        """Open additional window with current table."""
        current_table = self.main_window.tab_widget.tabText(self.main_window.tab_widget.currentIndex())
        from ui.additional_window import AdditionalWindow
        win = AdditionalWindow(self.main_window, current_table, self.main_window.db)
        win.closed.connect(self.search_controller.window_closed)
        self.search_controller.window_opened(win)
        win.show()

    def on_show_logs(self):
        """Open logs window."""
        from ui.logs_window import LogsWindow
        self.logs_window = LogsWindow()
        self.logs_window.show()

    def on_return_to_main(self):
        """Return to main simulator menu"""
        import subprocess
        import sys
        from pathlib import Path
        
        # way to laucher.py
        current_file = Path(__file__)  # .../Python/Database/Viewer_v2/ui/base_controller.py
        python_dir = current_file.parent.parent.parent.parent  
        launcher_path = python_dir / "launcher.py"
        
        print(f"Looking for launcher at: {launcher_path}")
        print(f"File exists: {launcher_path.exists()}")
        
        # Close additional windows
        if hasattr(self, 'search_controller'):
            for window in self.search_controller.additional_windows[:]:
                window.close()
        
        # Close Viewer
        self.main_window.close()
        
        # Launch launcher.py
        if launcher_path.exists():
            subprocess.Popen([sys.executable, str(launcher_path)])
            sys.exit(0)  # Close current process
        else:
            print(f"ERROR: launcher.py not found at {launcher_path}")
            # try main.py
            main_path = python_dir / "main.py"
            if main_path.exists():
                subprocess.Popen([sys.executable, str(main_path)])
                sys.exit(0)

    def on_exit(self):
        from PyQt6.QtWidgets import QMessageBox, QApplication
        msg = QMessageBox()
        msg.setWindowTitle("Critical ALERT")
        msg.setText("⚠️ Are you really sure you want to leave it????")
        msg.setIcon(QMessageBox.Icon.Warning)
        yes_button = msg.addButton("Yes!", QMessageBox.ButtonRole.YesRole)
        no_button = msg.addButton("NO", QMessageBox.ButtonRole.NoRole)
        msg.exec()
        if msg.clickedButton() == yes_button:
            QApplication.quit()

    def on_reset(self):
        """Destroy EVERYTHING"""
        # 1. Destroy all filter controllers
        for fc in self.filter_controllers.values():
            fc.clear_all()
        
        # 2. destroy highlight
        self.highlight.clear_all(self._all_tables())

        # 3. deactivate search if active
        if self.search_controller.search_active:
            self.main_window.side_menu.set_search_on(False)

        # 4. deactivate all side menu options
        sm = self.main_window.side_menu
        sm.grid_on.setChecked(True)
        sm.highlight_on.setChecked(True)
        sm.freeze_off.setChecked(True)
        sm.fullsize_off.setChecked(True)
        sm.filter_exact_cb.setChecked(False)
        sm.filter_case_cb.setChecked(False)

        # 5. deactivate freeze and fullsize for all tables
        for table in self._all_tables():
            table.pinned_rows.clear()
            table._rebuild_table()
            table.set_freeze_enabled(False)

        # 6. deactivate search and clear search input
        self.main_window.side_menu.search_input.clear()
    
        # 7. update status bar
        self.main_window.status_bar.showMessage("Reset to default state")

    def register_table(self, table_name, table_widget):
        """Create FilterController for a table."""
        from ui.filter_controller import FilterController
        fc = FilterController(table_widget)
        table_widget.filter_controller = fc
        self.filter_controllers[table_name] = fc

    def _on_filter_exact_toggled(self, enabled):
        for fc in self.filter_controllers.values():
            fc.set_exact_match(enabled)

    def _on_filter_case_toggled(self, enabled):
        for fc in self.filter_controllers.values():
            fc.set_case_sensitive(enabled)

    def update_filter_indicator(self):
        """update filter indicator in side menu."""
        active = any(len(fc.filters) > 0 for fc in self.filter_controllers.values())
        self.main_window.side_menu.set_filter_indicator(active)

    def connect_new_menu(self, menu):
        """Connect signals to menu when inoriginal table was choosed."""
        menu.grid_toggled.connect(self.grid.set_enabled)
        menu.highlight_toggled.connect(self._on_highlight_toggled)
        menu.fullsize_toggled.connect(self.main_window.fullsize_controller.toggle_fullsize)
        menu.freeze_rows_toggled.connect(self._on_freeze_toggled)
        menu.filter_exact_toggled.connect(self._on_filter_exact_toggled)
        menu.filter_case_toggled.connect(self._on_filter_case_toggled)
        
        # Buttons connection
        menu.connect_buttons(self)

    def on_find_database(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from pathlib import Path
        import sqlite3
        import config

        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Select Database File",
            str(config.DATABASE_DIR),
            "SQLite Database (*.db *.sqlite);;All Files (*)"
        )
        if not file_path:
            return

        try:
            # Close old connection
            if self.main_window.db and self.main_window.db.connection:
                self.main_window.db.close()

            # Connect to new database
            connection = sqlite3.connect(str(file_path))
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if not tables:
                QMessageBox.warning(self.main_window, "Warning", "Database has no tables.")
                connection.close()
                return

            # Update database connection
            self.main_window.db.connection = connection
            config.DB_PATH = Path(file_path)

            # Clear and reload tables
            self.main_window.tab_widget.clear()
            self.main_window.table_widgets.clear()
            self.main_window.load_tables()
            self.main_window.update_status_bar()

            # Re-register tables
            for table_name, table_widget in self.main_window.table_widgets.items():
                self.register_table(table_name, table_widget)

            self.main_window.status_bar.showMessage(f"Database loaded: {Path(file_path).name}")

            # Close additional windows
            for window in self.search_controller.additional_windows[:]:
                window.close()

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to load database:\n{str(e)}")


    def on_find_other_data(self):
        """Open Manufacturing data folder in file explorer."""
        import os
        import subprocess
        import sys
        from pathlib import Path
        from config import DATABASE_DIR

        manufacturing_dir = DATABASE_DIR / "Manufacturing data"
        # Create folder if it doesn't exist
        manufacturing_dir.mkdir(parents=True, exist_ok=True)

        try:
            if sys.platform == 'win32':
                os.startfile(str(manufacturing_dir))
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(manufacturing_dir)])
            else:
                subprocess.run(['xdg-open', str(manufacturing_dir)])
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Could not open folder:\n{str(e)}"
            )

    def setup_status_bar(self):
        """Create and configure status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("font-size: 9pt; color: #666;")
        self.update_status_bar()