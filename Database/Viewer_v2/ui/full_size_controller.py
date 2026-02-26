"""
Full Size Window controller.
Manages the full-screen table mode without side menu and tabs.
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QObject


class FullSizeController(QObject):
    """
    Controls the Full Size Window mode.
    When enabled, hides side menu and tab bar, shows only the current table.
    A small close button appears at bottom-right to exit the mode.
    """
    
    # Signal emitted when mode is exited via close button
    mode_exited = pyqtSignal()
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.is_active = False
        
        # Create close button (hidden initially)
        self.close_button = QPushButton("✕", main_window)
        self.close_button.setObjectName("fullsizeCloseButton")
        self.close_button.setFixedSize(40, 40)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.close_button.clicked.connect(self.exit_fullsize)
        self.close_button.hide()
        
    def enter_fullsize(self):
        """Enable full size mode."""
        if self.is_active:
            return
            
        # Hide side menu
        self.main_window.side_menu.hide()
        
        # Hide tab bar (but keep tab widget)
        self.main_window.tab_widget.tabBar().hide()
        
        # Show close button
        self.close_button.show()
        self._update_button_position()
        
        self.is_active = True
        
    def exit_fullsize(self):
        """Disable full size mode."""
        if not self.is_active:
            return
            
        # Show side menu
        self.main_window.side_menu.show()
        
        # Show tab bar
        self.main_window.tab_widget.tabBar().show()
        
        # Hide close button
        self.close_button.hide()
        
        self.is_active = False
        self.mode_exited.emit()
        
    def toggle_fullsize(self, enabled):
        """Toggle mode based on radio button."""
        if enabled:
            self.enter_fullsize()
        else:
            self.exit_fullsize()
            
    def _update_button_position(self):
        """Place close button at bottom-right corner of main window."""
        if not self.is_active:
            return
        # Get main window geometry
        rect = self.main_window.geometry()
        # Position button relative to main window's bottom-right
        x = rect.width() - self.close_button.width() - 20
        y = rect.height() - self.close_button.height() - 20
        self.close_button.move(x, y)
        
    def handle_resize(self, event):
        """Call this from main window's resizeEvent."""
        self._update_button_position()