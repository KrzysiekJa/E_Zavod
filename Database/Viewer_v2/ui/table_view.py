from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QAction

from config import TABLE_ROW_HEIGHT, TABLE_COLUMN_MIN_WIDTH
from styles.colors import (
    TABLE_HEADER, TABLE_GRID, TABLE_BACKGROUND, PINNED_ROW_COLOR,
    SEARCH_HIGHLIGHT, HIGHLIGHT_CELL, HIGHLIGHT_ROW, FILTER_ACTIVE_COLOR
)


class DatabaseTableView(QTableWidget):
    cell_highlight_requested = pyqtSignal(int, int)
    find_similar_requested = pyqtSignal(str)

    def __init__(self, table_name="", parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.highlight_enabled = True
        self.pinned_rows = []
        self.freeze_enabled = False
        self.original_data = []
        self.current_highlight = None
        self.filter_controller = None
        self.search_text = ""
        self.search_exact = False
        self.search_case = False
        self.search_active = False
        self.current_highlight_row = None
        self.current_highlight_col = None

        self._setup_ui()
        self._connect_signals()
        self._setup_header_context_menu()

    def _setup_ui(self):
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.setSortingEnabled(False)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)

        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(TABLE_ROW_HEIGHT)
        self.horizontalHeader().setMinimumSectionSize(TABLE_COLUMN_MIN_WIDTH)
        self.horizontalHeader().setStretchLastSection(False)

        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {TABLE_BACKGROUND};
                gridline-color: {TABLE_GRID};
            }}
            QHeaderView::section {{
                background-color: {TABLE_HEADER};
                padding: 6px;
                border: 1px solid #ccc;
                font-weight: bold;
            }}
        """)

    def _connect_signals(self):
        self.cellClicked.connect(self._on_cell_clicked)

    def _on_cell_clicked(self, row, col):
        if col == 0:
            return  # ignore clicks on a cell with a row number
        if self.highlight_enabled:
            if (self.current_highlight_row == row and 
                self.current_highlight_col == col):
                self.current_highlight_row = None
                self.current_highlight_col = None
                self._rebuild_table()
            else:
                self.current_highlight_row = row
                self.current_highlight_col = col
                self.cell_highlight_requested.emit(row, col)

    def set_highlight_enabled(self, enabled):
        self.highlight_enabled = enabled
        if not enabled:
            self.clearSelection()

    def load_data(self, column_names, data):
        if not column_names:
            return
        self.original_data = data
        self.column_names = column_names
        self._rebuild_table()

    def _rebuild_table(self):
        """Rebuild tables after freeze rows."""
        self.clear()
        self.setColumnCount(len(self.column_names) + 1)

        pinned_data = []
        unpinned_data = []

        for idx, row_data in enumerate(self.original_data):
            if idx in self.pinned_rows:
                pinned_data.append((idx, row_data))
            else:
                unpinned_data.append((idx, row_data))

        self.setRowCount(len(pinned_data) + len(unpinned_data))
        headers = ["№"] + self.column_names
        self.setHorizontalHeaderLabels(headers)

        row = 0
        for orig_idx, row_data in pinned_data:
            self._set_row_data(row, orig_idx, row_data, pinned=True)
            row += 1
        for orig_idx, row_data in unpinned_data:
            self._set_row_data(row, orig_idx, row_data, pinned=False)
            row += 1

        self._resize_columns()
        self.restore_search_highlight()

    def _set_row_data(self, row, orig_idx, row_data, pinned=False):
        """Fill in a row with fixed data."""
        item_num = QTableWidgetItem(str(orig_idx + 1))
        item_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item_num.setBackground(QColor(TABLE_HEADER))
        item_num.setForeground(QBrush(QColor("#000000")))
        item_num.setFlags(item_num.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item_num.setFlags(item_num.flags() & ~Qt.ItemFlag.ItemIsSelectable)  # selection forbidden
        self.setItem(row, 0, item_num)

        # Data column
        for c, value in enumerate(row_data):
            col_idx = c + 1
            item = QTableWidgetItem(str(value) if value is not None else "")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            if self.search_active and self.search_text:
                cell_str = str(value) if value is not None else ""
                if self.search_exact:
                    if self.search_case:
                        match = (cell_str == self.search_text)
                    else:
                        match = (cell_str.lower() == self.search_text.lower())
                else:
                    if self.search_case:
                        match = (self.search_text in cell_str)
                    else:
                        match = (self.search_text.lower() in cell_str.lower())
                if match:
                    item.setBackground(QColor(SEARCH_HIGHLIGHT))
                    self.setItem(row, col_idx, item)
                    continue

            if pinned:
                base_color = QColor(PINNED_ROW_COLOR)
            else:
                base_color = QColor("#ffffff") if row % 2 == 0 else QColor("#f5f5f5")

            is_highlight_cell = (row == self.current_highlight_row and col_idx == self.current_highlight_col)
            is_highlight_row = (row == self.current_highlight_row and col_idx != 0)
            is_highlight_column = (col_idx == self.current_highlight_col and row != self.current_highlight_row)

            if is_highlight_cell:
                item.setBackground(QColor(HIGHLIGHT_CELL))
            elif is_highlight_row or is_highlight_column:
                item.setBackground(QColor(HIGHLIGHT_ROW))
            else:
                item.setBackground(base_color)

            self.setItem(row, col_idx, item)

    def _resize_columns(self):
        self.setColumnWidth(0, 60)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        for col in range(1, self.columnCount()):
            self.resizeColumnToContents(col)
            if self.columnWidth(col) < TABLE_COLUMN_MIN_WIDTH:
                self.setColumnWidth(col, TABLE_COLUMN_MIN_WIDTH)

    # ============== FREEZE METHODS ==============
    def set_freeze_enabled(self, enabled):
        self.freeze_enabled = enabled
        if not enabled and self.pinned_rows:
            self.pinned_rows.clear()
            self._rebuild_table()

    def mouseDoubleClickEvent(self, event):
        if not self.freeze_enabled:
            super().mouseDoubleClickEvent(event)
            return

        index = self.indexAt(event.pos())
        if index.isValid() and index.column() == 0:
            displayed_row = index.row()
            item = self.item(displayed_row, 0)
            if item:
                orig_idx = int(item.text()) - 1
                if orig_idx in self.pinned_rows:
                    self.pinned_rows.remove(orig_idx)
                else:
                    self.pinned_rows.append(orig_idx)
                    self.pinned_rows.sort()
                self._rebuild_table()
            return

        super().mouseDoubleClickEvent(event)

    # ============== SEARCH METHODS ==============
    def set_search(self, text="", exact=False, case=False, active=False):
        self.search_text = text
        self.search_exact = exact
        self.search_case = case
        self.search_active = active
        self._rebuild_table()

    def count_search_matches(self, text, exact=False, case=False):
        if not text:
            return 0
        count = 0
        for row_data in self.original_data:
            for value in row_data:
                cell_str = str(value) if value is not None else ""
                if exact:
                    if case:
                        match = (cell_str == text)
                    else:
                        match = (cell_str.lower() == text.lower())
                else:
                    if case:
                        match = (text in cell_str)
                    else:
                        match = (text.lower() in cell_str.lower())
                if match:
                    count += 1
        return count

    def _is_search_match(self, cell_value):
        if not self.search_active or not self.search_text:
            return False
        if self.search_exact:
            if self.search_case:
                return (cell_value == self.search_text)
            else:
                return (cell_value.lower() == self.search_text.lower())
        else:
            if self.search_case:
                return (self.search_text in cell_value)
            else:
                return (self.search_text.lower() in cell_value.lower())

    def restore_search_highlight(self):
        if not self.search_active or not self.search_text:
            return
        for r in range(self.rowCount()):
            for c in range(1, self.columnCount()):
                item = self.item(r, c)
                if item and self._is_search_match(item.text()):
                    item.setBackground(QColor(SEARCH_HIGHLIGHT))

    # ============== CONTEXT MENU ==============
    def _setup_header_context_menu(self):
        header = self.horizontalHeader()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._show_header_context_menu)

    def _show_header_context_menu(self, pos):
        header = self.horizontalHeader()
        logical_index = header.logicalIndexAt(pos)
        if logical_index < 0:
            return

        menu = QMenu(self)

        # Copy column name
        copy_name_action = QAction("📋 Copy column name", self)
        copy_name_action.triggered.connect(lambda: self.copy_column_name(logical_index))
        menu.addAction(copy_name_action)

        # Copy column data
        copy_data_action = QAction("📋 Copy all column data", self)
        copy_data_action.triggered.connect(lambda: self.copy_column_data(logical_index))
        menu.addAction(copy_data_action)

        menu.addSeparator()

        filter_menu = menu.addMenu("Filter")
        custom_action = QAction("Custom value...", self)
        custom_action.triggered.connect(lambda: self._filter_custom(logical_index))
        filter_menu.addAction(custom_action)

        sort_menu = menu.addMenu("Sort")
        asc_action = QAction("A–Z", self)
        asc_action.triggered.connect(lambda: self._sort_column(logical_index, "asc"))
        sort_menu.addAction(asc_action)
        desc_action = QAction("Z–A", self)
        desc_action.triggered.connect(lambda: self._sort_column(logical_index, "desc"))
        sort_menu.addAction(desc_action)

        none_action = QAction("None", self)
        none_action.triggered.connect(lambda: self._clear_column(logical_index))
        menu.addAction(none_action)

        menu.exec(header.mapToGlobal(pos))

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return

        row = index.row()
        col = index.column()
        item = self.item(row, col)
        if not item:
            return

        cell_value = item.text()
        menu = QMenu(self)

        copy_action = QAction("Copy Value", self)
        copy_action.triggered.connect(lambda: self.copy_cell_value(cell_value))
        menu.addAction(copy_action)

        find_action = QAction("Find Similar", self)
        find_action.triggered.connect(lambda: self.find_similar(cell_value))
        menu.addAction(find_action)

        menu.addSeparator()

        reset_action = QAction("🔄 Reset everything", self)
        reset_action.triggered.connect(self.reset_all)
        menu.addAction(reset_action)

        menu.exec(event.globalPos())

    def copy_cell_value(self, value):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(value)

    def find_similar(self, value):
        self.find_similar_requested.emit(value)

    def reset_all(self):
        main_window = self.window()
        if hasattr(main_window, 'base_controller'):
            main_window.base_controller.on_reset()

    # ============== FILTER/SORT METHODS ==============
    def _filter_custom(self, column):
        from PyQt6.QtWidgets import QInputDialog
        col_name = self.horizontalHeaderItem(column).text() if self.horizontalHeaderItem(column) else f"Column {column}"
        text, ok = QInputDialog.getText(self, "Filter", f"Enter filter value for '{col_name}':")
        if ok and text is not None and self.filter_controller:
            data_col = column - 1
            self.filter_controller.set_column_filter(data_col, text.strip())
            self._update_header_color()
            self._update_header_filter_indicators()

    def _sort_column(self, column, order):
        if self.filter_controller:
            data_col = column - 1
            self.filter_controller.set_column_sort(data_col, order)
            self._update_header_color()

    def _clear_column(self, column):
        if self.filter_controller and column > 0:
            self.filter_controller.clear_column(column - 1)
            self._update_header_color()

    def _update_header_color(self):
        if not self.filter_controller:
            return
        header = self.horizontalHeader()
        header.setStyleSheet("")
        active_columns = set()
        active_columns.update(self.filter_controller.filters.keys())
        active_columns.update(self.filter_controller.sorts.keys())
        if not active_columns:
            return
        style = ""
        for col in active_columns:
            style += f"""
                QHeaderView::section:horizontal:{{{col+1}}} {{
                    background-color: {FILTER_ACTIVE_COLOR} !important;
                    font-weight: bold;
                }}
            """
        if style:
            header.setStyleSheet(style)

    def _update_header_filter_indicators(self):
        """Add filter and sort symbols to column headers."""
        if not self.filter_controller:
            return

        new_headers = ["№"]
        for col in range(len(self.column_names)):
            base_name = self.column_names[col]
            symbols = []
            

            if col in self.filter_controller.filters:
                symbols.append("🔽")
            
  
            if col in self.filter_controller.sorts:
                order = self.filter_controller.sorts[col]
                if order == "asc":
                    symbols.append("▲")   
                else:
                    symbols.append("▼")  
            
            if symbols:
                new_headers.append(f"{' '.join(symbols)} {base_name}")
            else:
                new_headers.append(base_name)
        
        self.setHorizontalHeaderLabels(new_headers)

    def _sort_column(self, column, order):
        if self.filter_controller:
            data_col = column - 1
            self.filter_controller.set_column_sort(data_col, order)
            self._update_header_color()
            self._update_header_filter_indicators()  

    def copy_column_name(self, column):
        header_item = self.horizontalHeaderItem(column)
        if header_item:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(header_item.text())

    def copy_column_data(self, column):
        data = []
        for row in range(self.rowCount()):
            item = self.item(row, column)
            if item:
                data.append(item.text())
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText("\n".join(data))

    # ============== GETTERS ==============
    def get_search_cells(self):
        cells = []
        if not self.search_active or not self.search_text:
            return cells
        for r in range(self.rowCount()):
            for c in range(1, self.columnCount()):
                item = self.item(r, c)
                if not item:
                    continue
                value = item.text()
                if self.search_exact:
                    if self.search_case:
                        match = (value == self.search_text)
                    else:
                        match = (value.lower() == self.search_text.lower())
                else:
                    if self.search_case:
                        match = (self.search_text in value)
                    else:
                        match = (self.search_text.lower() in value.lower())
                if match:
                    cells.append((r, c))
        return cells

    def restore_base_colors(self):
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                item = self.item(r, c)
                if not item:
                    continue
                if c == 0:
                    item.setBackground(QColor(TABLE_HEADER))
                else:
                    if r % 2 == 0:
                        item.setBackground(QColor("#ffffff"))
                    else:
                        item.setBackground(QColor("#f5f5f5"))
        
    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():

            menu = QMenu(self)
            reset_action = QAction("🔄 Reset everything", self)
            reset_action.triggered.connect(self.reset_all)
            menu.addAction(reset_action)
            menu.exec(event.globalPos())
            return

        row = index.row()
        col = index.column()
        item = self.item(row, col)
        if not item:
            return
        
        cell_value = item.text()
        menu = QMenu(self)

        copy_action = QAction("Copy Value", self)
        copy_action.triggered.connect(lambda: self.copy_cell_value(cell_value))
        menu.addAction(copy_action)

        find_action = QAction("Find Similar", self)
        find_action.triggered.connect(lambda: self.find_similar(cell_value))
        menu.addAction(find_action)

        menu.addSeparator()

        reset_action = QAction("🔄 Reset everything", self)
        reset_action.triggered.connect(self.reset_all)
        menu.addAction(reset_action)

        menu.exec(event.globalPos())