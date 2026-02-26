"""
QSS stylesheets for the application.
Combines all styles for different widgets.
"""

from styles.colors import *


def get_main_stylesheet():
    """
    Return main application stylesheet.
    Combines all styles for different widgets.
    """
    return f"""
    /* ============== MAIN WINDOW ============== */
    QMainWindow {{
        background-color: {MAIN_BACKGROUND};
    }}
    
    /* ============== TAB WIDGET ============== */
    QTabWidget::pane {{
        border: 1px solid #cccccc;
        background-color: {TABLE_HEADER};  /* Green background behind tables */
        top: -1px;
    }}
    
    QTabBar::tab {{
        background-color: {TAB_NORMAL};
        border: 1px solid #cccccc;
        border-bottom: none;
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        min-width: 120px;
        color: #333333;
    }}
    
    QTabBar::tab:selected {{
        background-color: {TAB_SELECTED};
        font-weight: bold;
        color: #000000;
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {TAB_HOVER};
    }}
    
    /* ============== TABLE VIEW ============== */
    QTableWidget {{
        gridline-color: {TABLE_GRID};
        alternate-background-color: {ALTERNATE_ROW};
        selection-background-color: {SELECTION_BLUE};
        font-size: 11pt;
        background-color: white;  /* Table content area is white */
    }}
    
    QTableWidget QTableCornerButton::section {{
        background-color: {TABLE_HEADER};
        border: 1px solid #cccccc;
    }}
    
    /* This ensures the area beyond the table is green */
    QScrollArea {{
        background-color: {TABLE_BACKGROUND};
    }}
    
    QHeaderView::section {{
        background-color: {TABLE_HEADER};
        padding: 6px;
        border: 1px solid #cccccc;
        font-weight: bold;
        font-size: 10pt;
    }}
    
    /* ============== SCROLLBARS (PURPLE) ============== */
    QScrollBar:vertical {{
        background-color: #f0f0f0;
        width: 16px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {SCROLLBAR};
        min-height: 30px;
        border-radius: 8px;
        margin: 3px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: #7b1fa2;
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background-color: #f0f0f0;
        height: 16px;
        margin: 0px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {SCROLLBAR};
        min-width: 30px;
        border-radius: 8px;
        margin: 3px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: #7b1fa2;
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}
    
    /* ============== STATUS BAR ============== */
    QStatusBar {{
        background-color: #f0f0f0;
        color: #333333;
        font-size: 9pt;
    }}
    
    QStatusBar::item {{
        border: none;
    }}
    
    /* ============== SIDE MENU (WILL BE ADDED) ============== */
    /* These styles will be used for the side menu */
    QFrame#sideMenu {{
        background-color: {SIDE_MENU_BACKGROUND};
        border-right: 2px solid {SIDE_BORDER};
    }}
    
    QLabel.sideMenuLabel {{
        color: {SIDE_MENU_TEXT};
        font-weight: bold;
        font-size: 10pt;
    }}
    
    QGroupBox.sideMenuGroup {{
        color: {SIDE_MENU_TEXT};
        border: 2px solid {SIDE_BORDER};
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }}
    
    QGroupBox::title.sideMenuGroup {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }}
    """