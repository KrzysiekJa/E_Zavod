from PyQt6.QtCore import QObject
from PyQt6.QtGui import QColor
from styles.colors import (
    TABLE_HEADER, HIGHLIGHT_CELL, HIGHLIGHT_ROW, HIGHLIGHT_COLUMN, ALTERNATE_ROW, SEARCH_HIGHLIGHT
)


class HighlightController(QObject):
    def __init__(self):
        super().__init__()
        self.enabled = True

    def set_enabled(self, enabled):
        self.enabled = enabled

    def highlight(self, table, row, col):
        """Highlight cell, row and column, preserving search highlights."""
        if not self.enabled or not table or col == 0:
            return

        if row is None or col is None:
            return

        # reset all color except search higlight
        self._reset_table_preserve_search(table)

        # light-blue row and column
        for c in range(1, table.columnCount()):
            item = table.item(row, c)
            if item and not table._is_search_match(item.text()):
                item.setBackground(QColor(HIGHLIGHT_ROW))

        # light-blue column
        for r in range(table.rowCount()):
            item = table.item(r, col)
            if item and not table._is_search_match(item.text()):
                item.setBackground(QColor(HIGHLIGHT_COLUMN))

        # fioletova cell
        cell = table.item(row, col)
        if cell and not table._is_search_match(cell.text()):
            cell.setBackground(QColor(HIGHLIGHT_CELL))

        # the first column (row numbers) should always be green
        for r in range(table.rowCount()):
            item = table.item(r, 0)
            if item:
                item.setBackground(QColor(TABLE_HEADER))
        
        # reapply search highlight if active
        table.restore_search_highlight()

    def clear_all(self, tables):
        for table in tables:
            self._reset_table(table)

    def _reset_table(self, table):
        for r in range(table.rowCount()):
            for c in range(table.columnCount()):
                item = table.item(r, c)
                if not item:
                    continue
                if c == 0:
                    item.setBackground(QColor(TABLE_HEADER))
                else:
                    if r % 2 == 0:
                        item.setBackground(QColor("#ffffff"))
                    else:
                        item.setBackground(QColor("#f5f5f5"))

    def _reset_table_preserve_search(self, table):
        """Reset table colors to default but preserve search highlights."""
        for r in range(table.rowCount()):
            for c in range(table.columnCount()):
                item = table.item(r, c)
                if not item:
                    continue
                
                # the first column (row numbers) and header row get a special color
                if c == 0:
                    item.setBackground(QColor(TABLE_HEADER))
                    continue
                
                # check if this cell is currently highlighted as a search match
                is_search = False
                if hasattr(table, '_is_search_match') and table.search_active:
                    is_search = table._is_search_match(item.text())
                
                if is_search:
                    # leave search highlights intact
                    continue
                else:
                    # alternate row coloring for better readability
                    if r % 2 == 0:
                        item.setBackground(QColor("#ffffff"))
                    else:
                        item.setBackground(QColor("#f5f5f5"))