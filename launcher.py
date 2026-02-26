#!/usr/bin/env python3
"""
Launcher for E-Zavod Simulator
Main menu with buttons to access different modules
"""
import sys
from pathlib import Path

# Add Python directory to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from PyQt6.QtWidgets import QApplication
from gui.main_menu import MainMenu


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_menu = None
        self.viewer = None
        
    def show_main_menu(self):
        """Show main menu with buttons"""
        if self.viewer:
            self.viewer.close()
            self.viewer = None
            
        # Create and show main menu
        self.main_menu = MainMenu(
            open_preview_callback=self.open_viewer,
            exit_callback=self.exit_app
        )
        self.main_menu.show()
        
    def open_viewer(self):
        """Open Database Viewer"""
        print("Opening Database Viewer...")
        
        # Hide main menu
        if self.main_menu:
            self.main_menu.hide()
        
        # Import and run Viewer
        try:
            # Option 1: Run as separate process (so it doesn't block)
            import subprocess
            viewer_path = BASE_DIR / "Database" / "Viewer_v2" / "app.py"
            subprocess.Popen([sys.executable, str(viewer_path)])
            
            # Show main menu again immediately
            self.show_main_menu()
            
        except Exception as e:
            print(f"Error opening viewer: {e}")
            self.show_main_menu()
        
    def exit_app(self):
        """Exit application"""
        self.app.quit()
        
    def run(self):
        """Start the application"""
        self.show_main_menu()
        return self.app.exec()


if __name__ == "__main__":
    controller = AppController()
    sys.exit(controller.run())