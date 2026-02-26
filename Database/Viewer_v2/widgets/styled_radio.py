"""
Custom styled radio buttons for side menu with better visibility.
"""

from PyQt6.QtWidgets import QRadioButton
from PyQt6.QtCore import Qt

from styles.colors import SIDE_MENU_TEXT, RADIO_CHECKED, RADIO_UNCHECKED


class StyledRadioButton(QRadioButton):
    """Radio button with custom styling for better visibility."""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Apply custom styling with distinct checked/unchecked states."""
        self.setStyleSheet(f"""
            QRadioButton {{
                color: {SIDE_MENU_TEXT};
                font-size: 11pt;  /* Larger font */
                font-weight: bold;
                spacing: 10px;
                padding: 5px;
            }}
            QRadioButton::indicator {{
                width: 20px;  /* Larger indicator */
                height: 20px;
                border-radius: 10px;
                border: 2px solid {RADIO_UNCHECKED};
            }}
            QRadioButton::indicator:unchecked {{
                background-color: transparent;
                border: 2px solid {RADIO_UNCHECKED};
            }}
            QRadioButton::indicator:checked {{
                background-color: {RADIO_CHECKED};  /* Dark green when checked */
                border: 2px solid {RADIO_CHECKED};
            }}
            QRadioButton:hover::indicator {{
                border: 2px solid #ffffff;
            }}
        """)