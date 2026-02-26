"""
Warning dialog shown when filter returns no visible rows.
"""

from PyQt6.QtWidgets import QMessageBox


class NoMatchesDialog:
    @staticmethod
    def show(column_name, filter_text, parent=None):
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("No matches")
        msg.setText(f"❌ No rows contain '<b>{filter_text}</b>' in column '{column_name}'.")
        msg.setInformativeText("Try another value or reset filter to NONE.")
        msg.exec()