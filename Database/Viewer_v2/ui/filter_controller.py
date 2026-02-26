from PyQt6.QtCore import QObject, Qt
from PyQt6.QtWidgets import QTableWidgetItem
from .no_matches_dialog import NoMatchesDialog
import re

class FilterController(QObject):
    """Manages per-column filters and sorts for a single table."""

    def __init__(self, table_view):
        super().__init__()
        self.table = table_view
        self.filters = {}          # column index -> filter text
        self.sorts = {}            # column index -> sort order ("asc", "desc")
        self.exact_match = False
        self.case_sensitive = False
        self.original_data = []    # store original data for restoration

    def set_exact_match(self, enabled):
        self.exact_match = enabled
        self.apply_filters()

    def set_case_sensitive(self, enabled):
        self.case_sensitive = enabled
        self.apply_filters()

    def set_column_filter(self, column, text):
        """Set filter text for a column. If text is empty, remove filter."""
        if text:
            self.filters[column] = text
        else:
            self.filters.pop(column, None)
        self.apply_filters()

    def set_column_sort(self, column, order):
        """Set sort order for a column. Only one column can be sorted at a time.
        If another column is already sorted, ignore the new sort request."""
        if order not in ("asc", "desc"):
            return

        # If sort exists in some columns, ignore it
        if self.sorts and list(self.sorts.keys())[0] != column:
            # Show optional menu
            print("Sorting already active on another column. Use 'None' or 'Reset' first.")
            return

        self.sorts[column] = order
        self.apply_filters()

    def clear_column(self, column):
        """Remove both filter and sort for a column."""
        self.filters.pop(column, None)
        self.sorts.pop(column, None)
        self.apply_filters()

    def clear_all(self):
        """Remove all filters and sorts."""
        self.filters.clear()
        self.sorts.clear()
        self.apply_filters()

    def _store_original_data(self):
        """Store current table data for restoration (excluding row numbers column)."""
        self.original_data = []
        for r in range(self.table.rowCount()):
            row = []
            # Beginning with 1, cause the first column is 0
            for c in range(1, self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.text() if item else "")
            self.original_data.append(row)
        
    def apply_filters(self):
        """Apply current filters and sorts to the table."""
        if not self.table:
            return

        # Store original data if not already stored
        if not self.original_data:
            self._store_original_data()

        # Get all rows
        rows = self.original_data[:]
        
        # Apply filters
        filtered_rows = []
        for row_data in rows:
            match = True
            for col, text in self.filters.items():
                if col >= len(row_data):
                    continue
                
                # Get cell value for filtering
                cell_value = row_data[col]
                
                # Convert to string for comparison, treating None as empty string
                cell_str = str(cell_value) if cell_value is not None else ""
                filter_text = str(text)
                
                if self.exact_match:
                    # exact match - check if they are equal
                    if self.case_sensitive:
                        match = (cell_str == filter_text)
                    else:
                        match = (cell_str.lower() == filter_text.lower())
                else:
                    # contains match - check if filter text is in cell value
                    if self.case_sensitive:
                        match = (filter_text in cell_str)
                    else:
                        match = (filter_text.lower() in cell_str.lower())
                
                if not match:
                    break
                    
            if match:
                filtered_rows.append(row_data)

        # Apply sort if any
        if self.sorts:
            # Get the first sort column (simplified - only one sort at a time)
            col = next(iter(self.sorts))
            order = self.sorts[col]
            reverse = (order == "desc")
            # natural sort key function
            def natural_key(value):
                if value is None:
                    return [""]
                value_str = str(value)
                return [int(part) if part.isdigit() else part.lower() 
                        for part in re.split(r'(\d+)', value_str)]
            
            filtered_rows.sort(
                key=lambda r: natural_key(r[col]) if col < len(r) else [""], 
                reverse=reverse
            )

        # Update table with filtered data
        self.table.setRowCount(len(filtered_rows))
        for r, row_data in enumerate(filtered_rows):

            item_num = QTableWidgetItem(str(r + 1))
            item_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_num.setFlags(item_num.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(r, 0, item_num)

            for c, value in enumerate(row_data):
                col_idx = c + 1  # shift +1
                item = self.table.item(r, col_idx)
                if item is None:
                    item = QTableWidgetItem()
                    self.table.setItem(r, col_idx, item)
                
                display_value = str(value) if value is not None else ""
                item.setText(display_value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Update colors
        from PyQt6.QtGui import QColor
        from styles.colors import TABLE_HEADER
        
        for r in range(self.table.rowCount()):
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if not item:
                    continue
                
                # First column (row numbers) gets special color
                if c == 0:
                    item.setBackground(QColor(TABLE_HEADER))
                    continue
                
                # Alternate row coloring
                if r % 2 == 0:
                    item.setBackground(QColor("#ffffff"))
                else:
                    item.setBackground(QColor("#f5f5f5"))

        # Restore search highlights if any
        if hasattr(self.table, 'restore_search_highlight'):
            self.table.restore_search_highlight()

        # Update header colors and filter indicators
        if hasattr(self.table, '_update_header_color'):
            self.table._update_header_color()
        if hasattr(self.table, '_update_header_filter_indicators'):
            self.table._update_header_filter_indicators()

        # Show no-matches dialog if needed
        if self.filters and len(filtered_rows) == 0:
            col, text = next(iter(self.filters.items()))
            # col+1 because header index = data column index + 1 (skip row numbers)
            col_name = self.table.horizontalHeaderItem(col + 1).text() if self.table.horizontalHeaderItem(col + 1) else f"Column {col}"
            NoMatchesDialog.show(col_name, text, self.table)

        # Update filter indicators in windows
        main_window = self.table.window()
        if hasattr(main_window, 'base_controller'):
            main_window.base_controller.update_filter_indicator()
        if hasattr(main_window, 'update_filter_indicator'):
            main_window.update_filter_indicator()

def natural_key(text):
    """Convert text into list of strings and integers for natural sorting."""
    if text is None:
        return [""]
    return [int(part) if part.isdigit() else part.lower() 
            for part in re.split(r'(\d+)', str(text))]