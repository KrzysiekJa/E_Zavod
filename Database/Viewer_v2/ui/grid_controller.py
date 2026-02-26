from PyQt6.QtCore import QObject

class GridController(QObject):
    """On/off grid visibility."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.enabled = True

    def set_enabled(self, enabled):
        self.enabled = enabled
        for table in self._all_tables():
            table.setShowGrid(enabled)
            table.viewport().update()

    def _all_tables(self):
        return list(self.main_window.table_widgets.values())