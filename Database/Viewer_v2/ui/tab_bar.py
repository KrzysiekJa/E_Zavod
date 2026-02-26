"""
Custom tab bar with navigation arrows for tables.
Implements requirements from section 2.2.2.
"""

from PyQt6.QtWidgets import QTabBar, QPushButton, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from config import TAB_ARROW_SIZE
from styles.colors import TAB_ARROWS


class CustomTabBar(QWidget):
    """
    Custom tab bar with navigation arrows.
    Shows arrows when tabs don't fit in available space.
    """
    
    # Signals
    tab_changed = pyqtSignal(int)  # Emitted when tab changes via arrows
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_widget = parent  # Reference to parent QTabWidget
        self.current_index = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the tab bar with arrows."""
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create left arrow button
        self.left_arrow = QPushButton("◀")
        self.left_arrow.setFixedSize(TAB_ARROW_SIZE, TAB_ARROW_SIZE)
        self.left_arrow.setStyleSheet(f"""
            QPushButton {{
                background-color: {TAB_ARROWS};
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)
        self.left_arrow.clicked.connect(self.navigate_left)
        self.left_arrow.setEnabled(False)
        
        # Tab bar will be managed by parent QTabWidget
        # We just provide the arrows
        
        # Create right arrow button
        self.right_arrow = QPushButton("▶")
        self.right_arrow.setFixedSize(TAB_ARROW_SIZE, TAB_ARROW_SIZE)
        self.right_arrow.setStyleSheet(f"""
            QPushButton {{
                background-color: {TAB_ARROWS};
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """)
        self.right_arrow.clicked.connect(self.navigate_right)
        self.right_arrow.setEnabled(False)
        
        # Add widgets to layout
        layout.addWidget(self.left_arrow)
        layout.addStretch()  # Tab bar will be inserted here by parent
        layout.addWidget(self.right_arrow)
        
    def navigate_left(self):
        """Navigate to previous tab."""
        if self.tab_widget and self.tab_widget.count() > 0:
            new_index = max(0, self.tab_widget.currentIndex() - 1)
            self.tab_widget.setCurrentIndex(new_index)
            self.tab_changed.emit(new_index)
            
    def navigate_right(self):
        """Navigate to next tab."""
        if self.tab_widget and self.tab_widget.count() > 0:
            new_index = min(self.tab_widget.count() - 1, 
                          self.tab_widget.currentIndex() + 1)
            self.tab_widget.setCurrentIndex(new_index)
            self.tab_changed.emit(new_index)
            
    def update_arrows(self):
        """Update arrow states based on current tab position."""
        if not self.tab_widget or self.tab_widget.count() == 0:
            self.left_arrow.setEnabled(False)
            self.right_arrow.setEnabled(False)
            return
            
        current_idx = self.tab_widget.currentIndex()
        total_tabs = self.tab_widget.count()
        
        # Enable/disable arrows
        self.left_arrow.setEnabled(current_idx > 0)
        self.right_arrow.setEnabled(current_idx < total_tabs - 1)