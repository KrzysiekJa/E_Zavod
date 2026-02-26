"""
Central settings manager for synchronizing between main and additional windows.
"""

from PyQt6.QtCore import QObject, pyqtSignal


class SettingsManager(QObject):
    """
    Manages global settings and notifies all windows of changes.
    """
    
    # Signals for settings changes
    grid_changed = pyqtSignal(bool)
    highlight_changed = pyqtSignal(bool)
    freeze_changed = pyqtSignal(bool)
    search_changed = pyqtSignal(str, bool, bool, bool)  # text, exact, case, active
    
    def __init__(self):
        super().__init__()
        self.grid_enabled = True
        self.highlight_enabled = True
        self.freeze_enabled = False
        self.search_text = ""
        self.search_exact = False
        self.search_case = False
        self.search_active = False
        
        self.windows = []  # the list of all windows (main + additional)
    
    def register_window(self, window):
        """Add window to the list."""
        if window not in self.windows:
            self.windows.append(window)
    
    def unregister_window(self, window):
        """Remove window from the list."""
        if window in self.windows:
            self.windows.remove(window)
    
    def set_grid(self, enabled):
        """Set grid state and notify all windows."""
        if self.grid_enabled != enabled:
            self.grid_enabled = enabled
            self.grid_changed.emit(enabled)
    
    def set_highlight(self, enabled):
        """Set highlight state and notify all windows."""
        if self.highlight_enabled != enabled:
            self.highlight_enabled = enabled
            self.highlight_changed.emit(enabled)
    
    def set_freeze(self, enabled):
        """Set freeze state and notify all windows."""
        if self.freeze_enabled != enabled:
            self.freeze_enabled = enabled
            self.freeze_changed.emit(enabled)
    
    def set_search(self, text, exact, case, active):
        """Set search parameters and notify all windows."""
        self.search_text = text
        self.search_exact = exact
        self.search_case = case
        self.search_active = active
        self.search_changed.emit(text, exact, case, active)