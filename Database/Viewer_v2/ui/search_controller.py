"""
Search controller – handles search logic, highlighting, and results list.
Connects side menu search controls with table views.
"""

from PyQt6.QtCore import QObject, pyqtSignal


class SearchController(QObject):
    """
    Manages search state across all tables.
    Emits signals when search parameters change.
    """
    
    # Signal emitted when a result table is clicked (to open additional window)
    table_selected = pyqtSignal(str)
    
    def __init__(self, main_window, side_menu):
        super().__init__()
        self.main_window = main_window
        self.side_menu = side_menu
        self.search_active = False
        self.search_text = ""
        self.exact_match = False
        self.case_sensitive = False
        self.additional_windows = []  # Keep track of open additional windows
        self._connect_signals()
        
    def _connect_signals(self):
        """Connect side menu signals to controller methods."""
        sm = self.side_menu
        sm.search_toggled.connect(self._on_search_toggled)
        sm.search_changed.connect(self._on_search_text_changed)
        sm.search_exact_toggled.connect(self._on_exact_toggled)
        sm.search_case_toggled.connect(self._on_case_toggled)
        sm.search_result_clicked.connect(self._on_result_clicked)
        
    def _on_search_toggled(self, enabled):
        """Search ON/OFF toggled."""
        self.search_active = enabled
        if enabled:
            # Show sub-options and results list in side menu
            self.side_menu.set_search_sub_visible(True)
            # Perform search with current parameters
            self._perform_search()
        else:
            # Clear search parameters and hide sub-options
            self.side_menu.search_input.clear()
            self.side_menu.set_search_sub_visible(False)
            self._clear_all_highlights()
            
    def _on_search_text_changed(self, text):
        """Search text entered."""
        self.search_text = text.strip()
        if self.search_active:
            self._perform_search()
            
    def _on_exact_toggled(self, enabled):
        """Exact match ON/OFF."""
        self.exact_match = enabled
        if self.search_active:
            self._perform_search()
            
    def _on_case_toggled(self, enabled):
        """Case sensitive ON/OFF."""
        self.case_sensitive = enabled
        if self.search_active:
            self._perform_search()
            
    def _perform_search(self):
        """
        Perform search across all tables.
        Updates highlighting and results list.
        """
        if not self.search_active or not self.search_text:
            self._clear_all_highlights()
            self.side_menu.update_search_results([])
            return
            
        results = []  # list of (table_name, match_count)
        
        # Get all table widgets
        tables = self.main_window.table_widgets
        
        for name, table in tables.items():
            # Count matches in this table
            count = table.count_search_matches(
                self.search_text,
                exact=self.exact_match,
                case=self.case_sensitive
            )
            results.append((name, count))
            # Apply highlighting to this table
            table.set_search(
                text=self.search_text,
                exact=self.exact_match,
                case=self.case_sensitive,
                active=True
            )
            
        # Update results list in side menu
        current = self.main_window.tab_widget.tabText(self.main_window.tab_widget.currentIndex())
        self.side_menu.update_search_results(results, current)

        # Also update additional windows
        for window in self.additional_windows:
            if window.table_widget:
                window.table_widget.set_search(
                    text=self.search_text,
                    exact=self.exact_match,
                    case=self.case_sensitive,
                    active=self.search_active
                )
        
    def _clear_all_highlights(self):
        """Turn off search highlighting in all tables."""
        for table in self.main_window.table_widgets.values():
            table.set_search(active=False)
        self.side_menu.update_search_results([])
        
    def _on_result_clicked(self, table_name):
        """Handle click on a table name in results list."""
        # For now, just print; later will open additional window
        from ui.additional_window import AdditionalWindow
        win = AdditionalWindow(self.main_window, table_name, self.main_window.db) 
        win.closed.connect(self.window_closed)
        self.window_opened(win)
        win.show()
        
    def activate_search_from_cell(self, value, exact=True, case=True):
        """
        Called from context menu 'Find Similar'.
        Sets search parameters and turns search ON.
        """
        self.side_menu.set_search_text(value)
        self.side_menu.set_search_exact(exact)
        self.side_menu.set_search_case(case)
        self.side_menu.set_search_on(True)
        # The signals will trigger _perform_search automatically
    

    def window_opened(self, window):
        """Register a new additional window."""
        self.additional_windows.append(window)
        # Apply current search to this window
        if self.search_active and self.search_text:
            window.table_widget.set_search(
                text=self.search_text,
                exact=self.exact_match,
                case=self.case_sensitive,
                active=True
            )
    
    def window_closed(self, window):
        """Unregister a closed additional window."""
        if window in self.additional_windows:
            self.additional_windows.remove(window)