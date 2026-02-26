"""
Main application window.
Contains side menu and tabbed table view.
"""

import sys
import config
from pathlib import Path
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QTabWidget, QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))
from ui.full_size_controller import FullSizeController 
from config import (
    APP_NAME, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
)
from styles.colors import MAIN_BACKGROUND
from core.database import DatabaseConnection
from ui.side_menu import SideMenu
from ui.base_controller import BaseController


class MainWindow(QMainWindow):
    """
    Main application window with side menu and table tabs.
    Implements full-screen light green background as per requirements.
    """

    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.current_table = ""
        self.table_widgets = {}
        
        self.setup_ui()
        self.load_tables()
        self.update_status_bar()

        self.base_controller = BaseController(self)
        self.side_menu.connect_buttons(self.base_controller)
        
        # Register tables
        for table_name, table_widget in self.table_widgets.items():
            self.base_controller.register_table(table_name, table_widget)
        
        # Connect signals
        for table_widget in self.table_widgets.values():
            table_widget.find_similar_requested.connect(
                self.base_controller.search_controller.activate_search_from_cell
            )
            table_widget.cell_highlight_requested.connect(
                self.base_controller._on_cell_clicked
            )
        
        self.fullsize_controller = FullSizeController(self)
        self.side_menu.fullsize_toggled.connect(self.fullsize_controller.toggle_fullsize)
        self.fullsize_controller.mode_exited.connect(self._on_fullsize_exited)

    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # === fixed side menu width on the left ===
        self.side_menu = SideMenu()
        self.side_menu.setFixedWidth(300)

        # === background color for the whole window ===
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(MAIN_BACKGROUND))
        self.setPalette(palette)

        # === central widget with horizontal layout ===
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # === main layout: side menu on the left, tab widget on the right ===
        self.main_layout = QHBoxLayout(central_widget)  # ← replaced with self.main_layout
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # === add side menu to the main layout ===
        self.main_layout.addWidget(self.side_menu)

        # === tabs widgets ===
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setMovable(True)
        self.main_layout.addWidget(self.tab_widget, 1)

        # === context menu for tabs ===
        self.setup_tab_context_menu()

        # === status bar ===
        self.setup_status_bar()

        # === hotkeys ===
        self.setup_shortcuts()
                
                
    def setup_status_bar(self):
        """Create and configure status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+F - acrivate search
        shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut.activated.connect(self.activate_search)

    def load_tables(self):
        """Load all tables from database into tabs with real data."""
        table_names = self.db.get_table_names()

        if not table_names:
            self.status_bar.showMessage("No tables found in database")
            return

        from core.table_loader import TableLoader
        from ui.table_view import DatabaseTableView
        from PyQt6.QtWidgets import QWidget, QVBoxLayout

        table_loader = TableLoader(self.db)

        loaded_count = 0
        for table_name in table_names:
            # Load table data
            columns, data, total_rows = table_loader.load_table_preview(table_name)

            # Create table widget
            table_widget = DatabaseTableView(table_name)

            if columns:
                table_widget.load_data(columns, data)
                loaded_count += 1

            # making a container for the table to allow adding other widgets later if needed (e.g. filter header)
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            # add table to container without stretch (it will take as much space as it needs, but won't stretch vertically if we add something below it)
            layout.addWidget(table_widget)

            # add container to tab widget
            self.tab_widget.addTab(container, table_name)
            self.table_widgets[table_name] = table_widget

        self.current_table = table_names[0] if table_names else ""
        self.update_status_bar()

    def _on_fullsize_exited(self):
        """Called when fullsize mode is exited via close button."""
        # Set radio button to OFF
        self.side_menu.fullsize_off.setChecked(True)

    def resizeEvent(self, event):
        """Override to update close button position."""
        super().resizeEvent(event)
        if hasattr(self, 'fullsize_controller'):
            self.fullsize_controller.handle_resize(event)

    def setup_tab_context_menu(self):
        """Setup right-click menu for tabs."""
        self.tab_widget.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_widget.tabBar().customContextMenuRequested.connect(self.show_tab_context_menu)

    def show_tab_context_menu(self, position):
        """Show context menu for tab bar."""
        tab_bar = self.tab_widget.tabBar()
        tab_index = tab_bar.tabAt(position)
        
        menu = QMenu(self)
        
        view_any_action = QAction("👁 View table...", self)
        view_any_action.triggered.connect(self.show_table_selector_dialog)
        menu.addAction(view_any_action)
        
        open_any_action = QAction("📂 Open table in new window...", self)
        open_any_action.triggered.connect(self.show_table_selector_for_new_window)
        menu.addAction(open_any_action)
        
        menu.exec(tab_bar.mapToGlobal(position))

    def show_table_selector_dialog(self):
        """Show dialog to select a table to view."""
        from PyQt6.QtWidgets import QInputDialog
        tables = list(self.table_widgets.keys())
        if not tables:
            return
        
        table_name, ok = QInputDialog.getItem(
            self, "Select Table", "Choose table:", tables, 0, False
        )
        if ok and table_name:
            # Finf tab index
            for i in range(self.tab_widget.count()):
                if self.tab_widget.tabText(i) == table_name:
                    self.tab_widget.setCurrentIndex(i)
                    break

    def show_table_selector_for_new_window(self):
        """Show dialog to select a table to open in new window."""
        from PyQt6.QtWidgets import QInputDialog
        tables = list(self.table_widgets.keys())
        if not tables:
            return
        
        table_name, ok = QInputDialog.getItem(
            self, "Select Table", "Choose table:", tables, 0, False
        )
        if ok and table_name:
            self.open_table_in_additional_window(table_name)

    def update_status_bar(self):
        """Update status bar with database info."""
        from pathlib import Path
        from config import DB_PATH
        
        # DB name
        if hasattr(self.db, 'db_path') and self.db.db_path:
            db_path = self.db.db_path
        else:
            db_path = DB_PATH
        
        db_name = Path(db_path).name
        
        # Original or not ?
        is_original = str(Path(db_path).resolve()) == str(Path(DB_PATH).resolve())
        status = "Original" if is_original else "⚠️ Unoriginal"
        
        # Tables amount
        table_count = len(self.table_widgets)
        
        # message forming
        message = f"{db_name} | {status} | {table_count} tables"
        
        self.status_bar.showMessage(message)
        self.status_bar.repaint()  # Forced restore
        print(f"Status: {message}")
            
    def setup_status_bar(self):
        """Create and configure status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setStyleSheet("font-size: 9pt;")
        self.update_status_bar()

    def open_table_in_additional_window(self, table_name):
        """Open additional window with selected table."""
        from ui.additional_window import AdditionalWindow
        win = AdditionalWindow(self, table_name, self.db)
        win.closed.connect(self.base_controller.search_controller.window_closed)
        self.base_controller.search_controller.window_opened(win)
        win.show()

    def activate_search(self):
        """Activate search and focus on input field."""
        # activate Search ON
        self.side_menu.set_search_on(True)
        self.side_menu.search_input.setFocus()