"""
Additional Window for viewing tables without side menu.
Only a dropdown to select table and a Return button.
Search, grid, highlight, freeze settings are synced with main window.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.table_view import DatabaseTableView
from styles.colors import BUTTON_RETURN, BUTTON_TEXT_COLOR, BUTTON_RESET

class AdditionalWindow(QWidget):
    """
    Additional window displaying a single table with minimal controls.
    """
    
    # Signal emitted when window is closed
    closed = pyqtSignal(object)  # emits self
    
    def __init__(self, main_window, table_name, db_connection):
        super().__init__()
        self.main_window = main_window
        self.db = db_connection
        self.current_table_name = table_name
        self.table_widget = None
        
        self.setWindowTitle(f"Additional View - {table_name}")
        self.setGeometry(200, 200, 800, 600)
        self.setMinimumSize(600, 400)
        
        self.setup_ui()
        self.load_table(table_name)
        
        # Connect to main window's controllers for sync
        self.connect_controllers()
        
  
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

    def setup_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)                # <--- THIS LINE IS ESSENTIAL
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Top bar with dropdown and buttons
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        # Table selector
        self.table_selector = QComboBox()
        self.table_selector.addItems(self.main_window.db.get_table_names())
        self.table_selector.setCurrentText(self.current_table_name)
        self.table_selector.currentTextChanged.connect(self.on_table_changed)

        # Filter indicator label (hidden initially)
        self.filter_indicator = QLabel("")
        self.filter_indicator.setStyleSheet("""
            QLabel {
                color: #ff4444;
                font-weight: bold;
                font-size: 10pt;
                padding: 3px 8px;
                background-color: #ffeeee;
                border: 1px solid #ff4444;
                border-radius: 3px;
            }
        """)
        self.filter_indicator.hide()

        # Button panel (Reset + Close)
        button_panel = QHBoxLayout()
        button_panel.setSpacing(5)

        # Reset Settings button
        self.reset_btn = QPushButton("🔄 RESET SETTINGS")
        self.reset_btn.setFixedSize(140, 30)
        self.reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_RESET};
                color: {BUTTON_TEXT_COLOR};
                font-weight: bold;
                font-size: 10pt;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(BUTTON_RESET)};
            }}
        """)
        self.reset_btn.clicked.connect(self.reset_settings)

        # Close Window button (ex RETURN)
        self.close_btn = QPushButton("❌ CLOSE WINDOW")
        self.close_btn.setFixedSize(140, 30)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_RETURN};
                color: {BUTTON_TEXT_COLOR};
                font-weight: bold;
                font-size: 10pt;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #aa00aa;
            }}
        """)
        self.close_btn.clicked.connect(self.close)

        button_panel.addWidget(self.reset_btn)
        button_panel.addWidget(self.close_btn)

        # Assemble top bar
        top_bar.addWidget(QLabel("Table:"))
        top_bar.addWidget(self.table_selector)
        top_bar.addStretch()
        top_bar.addWidget(self.filter_indicator)
        top_bar.addLayout(button_panel)

        layout.addLayout(top_bar)                  # <--- NOW layout IS DEFINED

        # Table view area
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table_container)

    def update_filter_indicator(self):
        """Restore filter indicator."""
        if hasattr(self, 'filter_controller') and self.filter_controller.filters:
            self.filter_indicator.setText("⚠️ FILTER ACTIVE")
            self.filter_indicator.show()
        else:
            self.filter_indicator.hide()
        
      
    def load_table(self, table_name):
        """Load specified table into view."""
        # Remove old table widget if exists
        if self.table_widget:
            self.table_layout.removeWidget(self.table_widget)
            self.table_widget.deleteLater()
            self.table_widget = None
            self.filter_controller = None
        
        # Create new table widget
        from core.table_loader import TableLoader
        from ui.filter_controller import FilterController
        loader = TableLoader(self.db)
        columns, data, total = loader.load_table_preview(table_name)
        
        # table creation
        self.table_widget = DatabaseTableView(table_name)
        
        # Create filter controller for this table
        self.filter_controller = FilterController(self.table_widget)
        self.table_widget.filter_controller = self.filter_controller
        
        # Connect signals for cell click and find similar
        self.table_widget.cell_highlight_requested.connect(self.on_cell_clicked)
        self.table_widget.find_similar_requested.connect(
            self.main_window.base_controller.search_controller.activate_search_from_cell
        )
        
        if columns:
            self.table_widget.load_data(columns, data)
        
        # Apply current settings from main window
        self.sync_settings()
        
        # add filter indicator update
        self.update_filter_indicator()
        
        self.table_layout.addWidget(self.table_widget)
        
    def on_table_changed(self, table_name):
        """Handle table selection change."""
        self.current_table_name = table_name
        self.setWindowTitle(f"Additional View - {table_name}")
        self.load_table(table_name)
        
    def connect_controllers(self):
        """Connect to main window's controllers to sync settings."""
        # Search controller
        self.main_window.base_controller.search_controller.window_opened(self)
        self.sync_settings()
        
    
    def sync_settings(self):
        """Apply current settings from main window."""
        if not self.table_widget:
            return
            
        sm = self.main_window.side_menu
        
        # Grid
        self.table_widget.setShowGrid(sm.grid_on.isChecked())
        
        # Highlight
        self.table_widget.set_highlight_enabled(sm.highlight_on.isChecked())
        
        # Freeze
        self.table_widget.set_freeze_enabled(sm.freeze_on.isChecked())
        
        # add: Filter options (Exact/Case)
        if hasattr(self, 'filter_controller'):
            self.filter_controller.set_exact_match(sm.filter_exact_cb.isChecked())
            self.filter_controller.set_case_sensitive(sm.filter_case_cb.isChecked())
        
        # Search - if active, apply
        if hasattr(self.main_window.base_controller, 'search_controller'):
            sc = self.main_window.base_controller.search_controller
            if sc.search_active and sc.search_text:
                self.table_widget.set_search(
                    text=sc.search_text,
                    exact=sc.exact_match,
                    case=sc.case_sensitive,
                    active=True
                )

    def closeEvent(self, event):
        """Override close event to notify main window."""
        self.closed.emit(self)
        super().closeEvent(event)

    def reset_all(self):
        """Reset all settings without closing the window."""
        # clear search
        if hasattr(self.main_window, 'search_controller'):
            # Search off
            self.main_window.side_menu.set_search_on(False)
            # clear search input
            self.main_window.side_menu.search_input.clear()
        
        # clear filters
        if self.table_widget:
            self.table_widget.pinned_rows.clear()
            self.table_widget._rebuild_table()
        
        # clear highlights if any
        self.table_widget.clearSelection()
        
        # update filter indicator
        self.update_status("Reset in additional window")

    def on_cell_clicked(self, row, col):
        """Handle cell click for highlighting."""
        if hasattr(self.main_window, 'base_controller'):
            if self.main_window.base_controller.highlight.enabled:
                self.main_window.base_controller.highlight.highlight(self.table_widget, row, col)

    def reset_settings(self):
        """
        Reset all settings for this window without closing it.
        Clears filters, search, pinned rows, and resets to default state.
        """
        # Clear filters if any
        if hasattr(self, 'filter_controller') and self.filter_controller:
            self.filter_controller.clear_all()
        
        # Turn off search if active
        if hasattr(self.main_window, 'search_controller'):
            self.main_window.side_menu.set_search_on(False)
            self.main_window.side_menu.search_input.clear()
        
        # Clear pinned rows
        if self.table_widget:
            self.table_widget.pinned_rows.clear()
            self.table_widget._rebuild_table()
        
        # Clear any selection
        self.table_widget.clearSelection()
        
        # Update filter indicator
        self.update_filter_indicator()
        
        # Show status in main window (optional)
        self.main_window.status_bar.showMessage("Settings reset in additional window")

    def _darken_color(self, hex_color, factor=0.8):
        """Darken hex color for hover effect."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"