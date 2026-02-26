"""
Side menu panel UI only.
Event handling will be in controls_manager.py.
"""
from PyQt6.QtWidgets import (
    QRadioButton, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLineEdit, QPushButton, QLabel, QFrame, 
    QScrollArea, QSizePolicy, QListWidget, QListWidgetItem, 
    QButtonGroup, QCheckBox  # added for filter options
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

from config import SIDE_MENU_WIDTH   
from styles.colors import (
    BUTTON_FIND_OTHER, RADIO_UNCHECKED, SIDE_MENU_BACKGROUND, SIDE_MENU_TEXT, SIDE_BORDER,
    SCROLLBAR, BUTTON_NORMAL, BUTTON_EDIT, BUTTON_REPORT, BUTTON_WINDOW, BUTTON_LOGS, BUTTON_RETURN, BUTTON_EXIT,
    BUTTON_TEXT_COLOR, BUTTON_FONT_WEIGHT, BUTTON_FONT_SIZE, BUTTON_RESET, RADIO_CHECKED
)
from widgets.styled_radio import StyledRadioButton
from styles.colors import BUTTON_FIND_DB, BUTTON_FIND_OTHER

class SideMenu(QWidget):
    """
    Left side menu UI only.
    Signals are emitted for controls manager.
    """
    
    # Signals for controls manager
    grid_toggled = pyqtSignal(bool)           # True for ON, False for OFF
    highlight_toggled = pyqtSignal(bool)      # True for ON
    filter_toggled = pyqtSignal(bool)         # True for ON
    fullsize_toggled = pyqtSignal(bool)       # True for ON, False for OFF
    freeze_rows_toggled = pyqtSignal(bool)    # True for ON
    
    # Signals for FILTER sub-options
    exact_toggled = pyqtSignal(bool)           # True for ON 
    case_toggled = pyqtSignal(bool)            # True for ON 
    
    # Signals for SEARCH
    search_changed = pyqtSignal(str)          # Search text
    search_toggled = pyqtSignal(bool)         # True for ON
    search_exact_toggled = pyqtSignal(bool)   # True for ON
    search_case_toggled = pyqtSignal(bool)    # True for ON
    search_result_clicked = pyqtSignal(str)   # Table name clicked

    filter_exact_toggled = pyqtSignal(bool)
    filter_case_toggled = pyqtSignal(bool)


    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.scroll_area.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj is self.scroll_area and event.type() == QEvent.Type.Wheel:
            # Forward the wheel event to the scroll area's wheelEvent
            self.scroll_area.wheelEvent(event)
            return True
        return super().eventFilter(obj, event)
    
            
    def setup_ui(self):
        """Initialize side menu UI."""
        self.setFixedWidth(SIDE_MENU_WIDTH)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {SIDE_MENU_BACKGROUND};
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(10)
        
        # Store scroll area as instance variable
        self.scroll_area = self.create_scroll_area()
        main_layout.addWidget(self.scroll_area)

    def create_scroll_area(self):
        """Create scroll area with all controls."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll_area.setStyleSheet(self.get_scrollbar_style())
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setSpacing(15)
        
        # Add all sections
        self.add_icon_section(container_layout)
        self.add_grid_section(container_layout)
        self.add_highlight_section(container_layout)
        self.add_filter_options_section(container_layout)
        self.add_fullsize_section(container_layout)
        self.add_freeze_rows_section(container_layout)
        self.add_search_section(container_layout)
        self.add_buttons_section(container_layout)
        
        # No stretch – container height = sum of sections
        # Scrollbar appears only if content exceeds viewport
        
        scroll_area.setWidget(container)
        return scroll_area
            
    def get_scrollbar_style(self):
        """Return scrollbar style with 20px right offset."""
        return f"""
            QScrollArea {{
                border: none;
                background-color: {SIDE_MENU_BACKGROUND};
            }}
            QScrollBar:vertical {{
                background-color: #f0f0f0;
                width: 20px;
                margin-left: 10px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {SCROLLBAR};
                min-height: 30px;
                border-radius: 6px;
                margin: 2px;
            }}
        """
        
    def add_icon_section(self, layout):
        """Add application icon from assets."""
        icon_frame = QFrame()
        icon_frame.setStyleSheet(f"""
            QFrame {{
                border-bottom: 0px solid {SIDE_BORDER};
                padding-bottom: 15px;
                margin-bottom: 10px;
            }}
        """)
    
        icon_layout = QVBoxLayout(icon_frame)
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.setSpacing(5)
    
        # Load icon from assets
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
        from pathlib import Path
        assets_dir = Path(__file__).parent.parent / "assets"
        icon_path = assets_dir / "icone.ico"
    
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            pixmap = pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio)
            icon_label.setPixmap(pixmap)
            icon_label.setStyleSheet(f"""
                QLabel {{
                    border: 1px solid {SIDE_BORDER};
                    border-radius: 1px;
                    padding: 5px;
                    background-color: white;
                }}
            """)
        else:
            icon_label.setText("🛠️")
            icon_label.setStyleSheet(f"""
                QLabel {{
                    color: {SIDE_MENU_TEXT};
                    font-size: 48pt;
                }}
            """)
    
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_frame)
        
    def add_grid_section(self, layout):
        """Grid ON/OFF section."""
        group = self.create_group_box("Grid")
        group_layout = QHBoxLayout(group)
        
        self.grid_on = StyledRadioButton("ON")
        self.grid_on.setChecked(True)
        self.grid_on.toggled.connect(lambda checked: self.grid_toggled.emit(checked))
        
        self.grid_off = StyledRadioButton("OFF")
        self.grid_off.toggled.connect(lambda checked: self.grid_toggled.emit(not checked))
        
        group_layout.addWidget(self.grid_on)
        group_layout.addWidget(self.grid_off)
        group_layout.addStretch()
        
        layout.addWidget(group)
        
    def add_highlight_section(self, layout):
        """Highlight cell ON/OFF section."""
        group = self.create_group_box("Highlight cell")
        group_layout = QHBoxLayout(group)
    
        self.highlight_on = StyledRadioButton("ON")
        self.highlight_on.setChecked(True)
        self.highlight_on.toggled.connect(lambda checked: self.highlight_toggled.emit(checked))
    
        self.highlight_off = StyledRadioButton("OFF")
        self.highlight_off.toggled.connect(lambda checked: self.highlight_toggled.emit(not checked))
    
        group_layout.addWidget(self.highlight_on)
        group_layout.addWidget(self.highlight_off)
        group_layout.addStretch()
    
        layout.addWidget(group)
        
    def add_freeze_rows_section(self, layout):
        """Freeze rows section."""
        group = self.create_group_box("Freeze rows")
        group_layout = QHBoxLayout(group)
        
        self.freeze_on = StyledRadioButton("ON")
        self.freeze_on.toggled.connect(lambda checked: self.freeze_rows_toggled.emit(checked))
        
        self.freeze_off = StyledRadioButton("OFF")
        self.freeze_off.setChecked(True)
        self.freeze_off.toggled.connect(lambda checked: self.freeze_rows_toggled.emit(not checked))
        
        group_layout.addWidget(self.freeze_on)
        group_layout.addWidget(self.freeze_off)
        group_layout.addStretch()
        
        layout.addWidget(group)
        
    def add_search_section(self, layout):
        """Search value section with sub-options and results list."""
        group = self.create_group_box("Search value")
        main_layout = QVBoxLayout(group)
        main_layout.setSpacing(10)

        # --- Search input ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter value to search...")
        self.search_input.textChanged.connect(self.search_changed.emit)
        main_layout.addWidget(self.search_input)

        # --- ON/OFF radio buttons ---
        toggle_layout = QHBoxLayout()
        self.search_on = StyledRadioButton("ON")
        self.search_off = StyledRadioButton("OFF")
        self.search_off.setChecked(True)

        # Group them so only one can be selected
        self.search_group = QButtonGroup(self)
        self.search_group.addButton(self.search_on, 1)
        self.search_group.addButton(self.search_off, 0)
        self.search_group.buttonToggled.connect(self._on_search_group_toggled)

        toggle_layout.addWidget(self.search_on)
        toggle_layout.addWidget(self.search_off)
        toggle_layout.addStretch()
        main_layout.addLayout(toggle_layout)

        # --- Sub-options (initially hidden) ---
        self.search_sub_widget = QWidget()
        sub_layout = QVBoxLayout(self.search_sub_widget)
        sub_layout.setContentsMargins(0, 5, 0, 0)
        sub_layout.setSpacing(8)

        # Exact match group
        exact_group = self.create_group_box("Search exact values")
        exact_group.setStyleSheet(exact_group.styleSheet() + "font-size: 9pt; margin-top: 8px;")
        exact_layout = QHBoxLayout(exact_group)
        exact_layout.setContentsMargins(10, 5, 5, 5)

        self.search_exact_on = StyledRadioButton("ON")
        self.search_exact_off = StyledRadioButton("OFF")
        self.search_exact_off.setChecked(True)
        self.search_exact_on.toggled.connect(lambda checked: self.search_exact_toggled.emit(checked))
        self.search_exact_off.toggled.connect(lambda checked: self.search_exact_toggled.emit(not checked))

        exact_layout.addWidget(self.search_exact_on)
        exact_layout.addWidget(self.search_exact_off)
        exact_layout.addStretch()
        sub_layout.addWidget(exact_group)

        # Case sensitive group
        case_group = self.create_group_box("Case sensitive")
        case_group.setStyleSheet(case_group.styleSheet() + "font-size: 9pt; margin-top: 8px;")
        case_layout = QHBoxLayout(case_group)
        case_layout.setContentsMargins(10, 5, 5, 5)

        self.search_case_on = StyledRadioButton("ON")
        self.search_case_off = StyledRadioButton("OFF")
        self.search_case_off.setChecked(True)
        self.search_case_on.toggled.connect(lambda checked: self.search_case_toggled.emit(checked))
        self.search_case_off.toggled.connect(lambda checked: self.search_case_toggled.emit(not checked))

        case_layout.addWidget(self.search_case_on)
        case_layout.addWidget(self.search_case_off)
        case_layout.addStretch()
        sub_layout.addWidget(case_group)

        # Results list
        self.search_results_list = QListWidget()
        self.search_results_list.setMaximumHeight(150)
        self.search_results_list.itemClicked.connect(self._on_result_item_clicked)
        sub_layout.addWidget(self.search_results_list)

        main_layout.addWidget(self.search_sub_widget)
        self.search_sub_widget.setVisible(False)

        layout.addWidget(group)

    def add_buttons_section(self, layout):
        """Add control buttons section."""
        group = self.create_group_box("Actions")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)
        
        # Create buttons
        buttons = [
            ("🔄 Reset", "reset", BUTTON_RESET),
            ("📝 Edit Database", "edit_db", BUTTON_EDIT),
            ("📊 Print Report", "print_report", BUTTON_REPORT),
            ("➕ Additional Window", "add_window", BUTTON_WINDOW),
            ("📋 LOGs", "show_logs", BUTTON_LOGS),
            ("🔍 Find Database", "find_db", BUTTON_FIND_DB),      
            ("📂 Find other data", "find_other", BUTTON_FIND_OTHER),
            ("🏠 Return to MAIN", "return_main", BUTTON_RETURN),
            ("❌ EXIT", "exit_app", BUTTON_EXIT),
        ]
        
        for text, name, color in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {BUTTON_TEXT_COLOR};
                    border: none;
                    padding: 12px;
                    border-radius: 5px;
                    font-weight: {BUTTON_FONT_WEIGHT};
                    font-size: {BUTTON_FONT_SIZE};
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {self._darken_color(color)};
                    border: 1px solid #000000;
                }}
            """)
            btn.setObjectName(name)
            group_layout.addWidget(btn)
        
        layout.addWidget(group)
        
    def add_filter_options_section(self, layout):
        """Add global filter options: Exact match and Case sensitive."""
        group = self.create_group_box("Filter options")
        group_layout = QVBoxLayout(group)

        # add checkboxes for filter options
        self.filter_exact_cb = QCheckBox("Exact match")
        self.filter_exact_cb.stateChanged.connect(self.on_exact_changed)
        group_layout.addWidget(self.filter_exact_cb)

        self.filter_case_cb = QCheckBox("Case sensitive")
        self.filter_case_cb.stateChanged.connect(self.on_case_changed)
        group_layout.addWidget(self.filter_case_cb)

        #add spacing and indicator for filter status
        group_layout.addSpacing(10)

        # filter status indicator
        self.filter_indicator = QLabel("")
        self.filter_indicator.setStyleSheet("""
            QLabel {
                color: #ff4444;
                font-weight: bold;
                font-size: 11pt;
                padding: 5px;
                background-color: #ffeeee;
                border: 1px solid #ff4444;
                border-radius: 3px;
            }
        """)
        self.filter_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.filter_indicator.hide()  # initially hidden
        group_layout.addWidget(self.filter_indicator)

        # custom styling for checkboxes
        self.style_checkboxes()

        layout.addWidget(group)

    def style_checkboxes(self):
        """Apply custom styling to filter option checkboxes."""
        style = f"""
            QCheckBox {{
                color: {SIDE_MENU_TEXT};
                font-size: 11pt;
                font-weight: bold;
                spacing: 10px;
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid {RADIO_UNCHECKED};
            }}
            QCheckBox::indicator:unchecked {{
                background-color: transparent;
                border: 2px solid {RADIO_UNCHECKED};
            }}
            QCheckBox::indicator:checked {{
                background-color: {RADIO_CHECKED};
                border: 2px solid {RADIO_CHECKED};
            }}
            QCheckBox:hover::indicator {{
                border: 2px solid #ffffff;
            }}
        """
        self.filter_exact_cb.setStyleSheet(style)
        self.filter_case_cb.setStyleSheet(style)

    def add_fullsize_section(self, layout):
        """Full Size Mode ON/OFF section."""
        group = self.create_group_box("Full Size Mode")
        group_layout = QHBoxLayout(group)
    
        self.fullsize_on = StyledRadioButton("ON")
        self.fullsize_off = StyledRadioButton("OFF")
        self.fullsize_off.setChecked(True)
    
        self.fullsize_on.toggled.connect(lambda checked: self.fullsize_toggled.emit(checked) if checked else None)
        self.fullsize_off.toggled.connect(lambda checked: self.fullsize_toggled.emit(not checked) if checked else None)
    
        group_layout.addWidget(self.fullsize_on)
        group_layout.addWidget(self.fullsize_off)
        group_layout.addStretch()
    
        layout.addWidget(group)
        
    def create_group_box(self, title):
        """Helper to create styled group box."""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {SIDE_MENU_TEXT};
                border: 2px solid {SIDE_BORDER};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 18px;
                font-weight: bold;
                font-size: 11pt;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 10px 0 10px;
            }}
        """)
        return group
    
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

    def connect_buttons(self, controller):
        """Connect side menu buttons to controller actions."""
        for child in self.findChildren(QPushButton):
            obj_name = child.objectName()
            if obj_name == "edit_db":
                child.clicked.connect(controller.on_edit_database)
            elif obj_name == "reset":
                child.clicked.connect(controller.on_reset)
            elif obj_name == "print_report":
                child.clicked.connect(controller.on_print_report)
            elif obj_name == "add_window":
                child.clicked.connect(controller.on_additional_window)
            elif obj_name == "show_logs":
                child.clicked.connect(controller.on_show_logs)
            elif obj_name == "find_db":
                child.clicked.connect(controller.on_find_database)
            elif obj_name == "return_main":
                child.clicked.connect(controller.on_return_to_main)
            elif obj_name == "exit_app":
                child.clicked.connect(controller.on_exit)
            elif obj_name == "find_other":
                child.clicked.connect(controller.on_find_other_data)

    def set_filter_options_visible(self, visible):
        """Show/hide filter sub-options."""
        if hasattr(self, 'filter_options_widget'):
            self.filter_options_widget.setVisible(visible)

    def set_filter_indicator(self, enabled):
        """show or hide filter enabled indicator."""
        if enabled:
            self.filter_indicator.setText("⚠️ FILTER ENABLED ⚠️")
            self.filter_indicator.show()
        else:
            self.filter_indicator.hide()

    def _on_filter_group_toggled(self, button, checked):
        """Handle main filter ON/OFF toggle."""
        if not checked:
            return
        if button == self.filter_on:
            self.filter_toggled.emit(True)
        else:
            self.filter_toggled.emit(False)

    # ============== NEW SEARCH METHODS ==============
    def _on_search_group_toggled(self, button, checked):
        """Handle main search ON/OFF toggle."""
        if not checked:
            return
        if button == self.search_on:
            self.search_toggled.emit(True)
        else:
            self.search_toggled.emit(False)

    def set_search_sub_visible(self, visible):
        """Show/hide search sub-options and results list."""
        self.search_sub_widget.setVisible(visible)

    def update_search_results(self, results, current_table_name=""):
        """
        Update the results list with table names and match counts.
        Only shows tables with count > 0.
        results: list of (table_name, count)
        current_table_name: name of currently selected table (to be shown bold)
        """
        self.search_results_list.clear()
        if not results:
            return

        # filter only where count > 0
        filtered_results = [(name, count) for name, count in results if count > 0]
        
        if not filtered_results:
            return  # nothing to show

        # Sort results: current first, then alphabetically
        current_item = None
        others = []
        for name, count in filtered_results:
            if name == current_table_name:
                current_item = (name, count)
            else:
                others.append((name, count))
        others.sort(key=lambda x: x[0])

        sorted_results = []
        if current_item:
            sorted_results.append(current_item)
        sorted_results.extend(others)

        # Add to list widget
        for name, count in sorted_results:
            item_text = f"{name} ({count})"
            item = QListWidgetItem(item_text)
            if name == current_table_name:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            self.search_results_list.addItem(item)

    def _on_result_item_clicked(self, item):
        """Emit signal with table name when an item is clicked."""
        text = item.text()
        # Extract table name before the first '('
        table_name = text.split(' (')[0]
        self.search_result_clicked.emit(table_name)

    def set_search_text(self, text):
        """Set search input text (used by Find Similar)."""
        self.search_input.setText(text)

    def set_search_exact(self, enabled):
        """Set exact match radio (used by Find Similar)."""
        if enabled:
            self.search_exact_on.setChecked(True)
        else:
            self.search_exact_off.setChecked(True)

    def set_search_case(self, enabled):
        """Set case sensitive radio (used by Find Similar)."""
        if enabled:
            self.search_case_on.setChecked(True)
        else:
            self.search_case_off.setChecked(True)

    def set_search_on(self, enabled):
        """Turn search ON/OFF programmatically."""
        if enabled:
            self.search_on.setChecked(True)
        else:
            self.search_off.setChecked(True)
    def on_exact_changed(self, state):
        """Handle exact match checkbox state change."""
        enabled = (state == 2)  # 2 this Qt.CheckState.Checked
        self.filter_exact_toggled.emit(enabled)

    def on_case_changed(self, state):
        """Handle case sensitive checkbox state change."""
        enabled = (state == 2)  # 2 this Qt.CheckState.Checked
        self.filter_case_toggled.emit(enabled)


            
    def add_simple_buttons(self, layout):
        """Add only essential buttons for missing DB state."""
        from styles.colors import BUTTON_FIND_DB, BUTTON_EXIT, BUTTON_TEXT_COLOR

        # Find Database button
        self.find_db_btn = QPushButton("🔍 FIND DATABASE")
        self.find_db_btn.setObjectName("find_db")
        self.find_db_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_FIND_DB};
                color: {BUTTON_TEXT_COLOR};
                border: none;
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(BUTTON_FIND_DB)};
            }}
        """)
        layout.addWidget(self.find_db_btn)
        # Exit button
        self.exit_btn = QPushButton("❌ EXIT")
        self.exit_btn.setObjectName("exit_app")
        self.exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {BUTTON_EXIT};
                color: {BUTTON_TEXT_COLOR};
                border: none;
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(BUTTON_EXIT)};
            }}
        """)
        layout.addWidget(self.exit_btn)

    def _clear_layout(self, layout):
        """Clean-up the layout recursively"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self._clear_layout(item.layout())

    