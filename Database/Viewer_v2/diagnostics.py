#!/usr/bin/env python3
"""
Diagnostics tool for Database Viewer filter and sort issues.
Run this script with the viewer open to analyze the problem.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QTextEdit, QLabel
from PyQt6.QtCore import Qt

from ui.table_view import DatabaseTableView
from ui.filter_controller import FilterController


class DiagnosticsDialog(QDialog):
    def __init__(self, table_widget):
        super().__init__()
        self.table = table_widget
        self.setWindowTitle("Filter/Sort Diagnostics")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(self)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFontFamily("Courier New")
        layout.addWidget(self.log)
        
        btn_refresh = QPushButton("🔄 Refresh Diagnostics")
        btn_refresh.clicked.connect(self.run_diagnostics)
        layout.addWidget(btn_refresh)
        
        self.run_diagnostics()
    
    def log_line(self, text):
        self.log.append(text)
        print(text)  # Also print to console
    
    def run_diagnostics(self):
        self.log.clear()
        self.log_line("=" * 60)
        self.log_line("DIAGNOSTICS: Filter and Sort")
        self.log_line("=" * 60)
        
        # 1. Basic table info
        self.log_line(f"\n📋 Table: {getattr(self.table, 'table_name', 'unknown')}")
        self.log_line(f"   Column count (including row numbers): {self.table.columnCount()}")
        
        # 2. Header names and indices
        self.log_line("\n📌 HEADER INDICES:")
        for col in range(self.table.columnCount()):
            item = self.table.horizontalHeaderItem(col)
            text = item.text() if item else "None"
            self.log_line(f"   Header[{col}] = '{text}'")
        
        # 3. Column names (data columns, without row number)
        if hasattr(self.table, 'column_names'):
            self.log_line("\n📊 DATA COLUMN NAMES:")
            for i, name in enumerate(self.table.column_names):
                self.log_line(f"   data_col[{i}] = '{name}'")
        else:
            self.log_line("\n❌ No column_names attribute!")
        
        # 4. Filter controller state
        fc = self.table.filter_controller
        if fc:
            self.log_line("\n🔍 FILTER CONTROLLER STATE:")
            self.log_line(f"   exact_match: {fc.exact_match}")
            self.log_line(f"   case_sensitive: {fc.case_sensitive}")
            self.log_line(f"   filters: {fc.filters}")
            self.log_line(f"   sorts: {fc.sorts}")
            self.log_line(f"   original_data size: {len(fc.original_data) if fc.original_data else 0}")
        else:
            self.log_line("\n❌ No filter_controller!")
        
        # 5. Check mapping between header indices and data column indices
        self.log_line("\n🔗 HEADER TO DATA COLUMN MAPPING:")
        for col in range(1, self.table.columnCount()):  # skip row number column
            data_col = col - 1
            header_item = self.table.horizontalHeaderItem(col)
            header_text = header_item.text() if header_item else "None"
            data_name = self.table.column_names[data_col] if hasattr(self.table, 'column_names') and data_col < len(self.table.column_names) else "unknown"
            self.log_line(f"   Header[{col}] '{header_text}' → data_col[{data_col}] '{data_name}'")
        
        # 6. If filters are active, check if they match the displayed indicators
        if fc and fc.filters:
            self.log_line("\n⚠️ ACTIVE FILTERS CHECK:")
            for data_col, value in fc.filters.items():
                header_index = data_col + 1
                header_item = self.table.horizontalHeaderItem(header_index)
                header_text = header_item.text() if header_item else "None"
                self.log_line(f"   Filter on data_col[{data_col}] = '{value}'")
                self.log_line(f"   → Should be shown on header[{header_index}] = '{header_text}'")
                # Check if header has 🔽 symbol
                has_filter_indicator = "🔽" in header_text if header_text else False
                self.log_line(f"   → Header has 🔽: {has_filter_indicator}")
        
        # 7. Check sort state
        if fc and fc.sorts:
            self.log_line("\n🔽 ACTIVE SORTS CHECK:")
            for data_col, order in fc.sorts.items():
                header_index = data_col + 1
                header_item = self.table.horizontalHeaderItem(header_index)
                header_text = header_item.text() if header_item else "None"
                self.log_line(f"   Sort on data_col[{data_col}] = {order}")
                self.log_line(f"   → Should be on header[{header_index}] = '{header_text}'")
                # Check if data is actually sorted
                if len(fc.original_data) > 1:
                    col_data = [row[data_col] for row in fc.original_data if data_col < len(row)]
                    sorted_col = sorted(col_data, reverse=(order=="desc"))
                    self.log_line(f"   First 3 values: {col_data[:3]}")
                    self.log_line(f"   Should be: {sorted_col[:3]}")
        else:
            self.log_line("\n🔽 No active sorts")
            
        # 8. Test filter method
        self.log_line("\n🧪 SIMULATING FILTER CALL:")
        self.log_line("   To test, click 'Test Filter' button below")
        
        # 9. Check if _update_header_filter_indicators would produce correct headers
        self.log_line("\n🎯 PREDICTED HEADERS (if updated now):")
        predicted = ["№"]
        for i, name in enumerate(self.table.column_names):
            if fc and i in fc.filters:
                predicted.append(f"🔽 {name}")
            else:
                predicted.append(name)
        self.log_line(f"   Predicted: {predicted}")
        
        # 10. Current actual headers
        current = []
        for col in range(self.table.columnCount()):
            item = self.table.horizontalHeaderItem(col)
            current.append(item.text() if item else "None")
        self.log_line(f"   Actual:    {current}")
        
        self.log_line("\n" + "=" * 60)
        self.log_line("To fix filter shift, ensure in _filter_custom you subtract 1: data_col = column - 1")
        self.log_line("To fix sort, check if filter_controller.set_column_sort is called and apply_filters applies sort.")


def run_diagnostics_on_table(table):
    """Run diagnostics dialog for a given table."""
    dialog = DiagnosticsDialog(table)
    dialog.exec()


if __name__ == "__main__":
    # If run directly, we need to attach to an existing viewer instance.
    # This is tricky; better to import and call from within the viewer.
    print("Please run this script from within the viewer by adding a button or shortcut.")
    print("Example: add a button in side menu that calls run_diagnostics_on_table(current_table)")