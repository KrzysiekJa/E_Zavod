import sys
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, 
    QApplication, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

# Import DatabaseMenu
from .database_menu import DatabaseMenu


class MainMenu(QWidget):
    def __init__(self, open_preview_callback, exit_callback):
        super().__init__()
        self.open_preview_callback = open_preview_callback
        self.exit_callback = exit_callback
        
        self.setWindowTitle("E-Zavod Simulator")
        self.resize(900, 800)
        
        # Set Icone
        icon_path = Path(__file__).parent.parent / "icone.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Window Style
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f3e5f5, stop:0.5 #e1bee7, stop:1 #ce93d8);
                border-radius: 20px;
            }
        """)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(50, 30, 50, 30)

        # Logo
        logo = self.create_logo()
        layout.addWidget(logo)

        # Title
        title = QLabel("E_ZAVOD SIMULATOR")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #4A148C;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 5px;
                margin: 10px 0 10px 0;
            }
        """)
        layout.addWidget(title)

        # Buttons
        buttons_info = [
            ("Simulator", self.open_simulator_menu, 
             ["#e1bee7", "#ce93d8", "#ba68c8"], "🏭"),      
            ("Database", self.open_database_menu,
             ["#ce93d8", "#ba68c8", "#ab47bc"], "🗄"),     
            ("Settings", self.open_settings,
             ["#ba68c8", "#ab47bc", "#9c27b0"], "⚙"),     
            ("Analytics", self.open_analytics,
             ["#ab47bc", "#9c27b0", "#8e24aa"], "📊"),     
            ("User guide", self.open_user_guide,
             ["#9c27b0", "#8e24aa", "#7b1fa2"], "📚"),   
            ("Users", self.open_users,
             ["#8e24aa", "#7b1fa2", "#6a1b9a"], "👥"),     
        ]

        for text, callback, colors, emoji in buttons_info:
            btn = self.create_styled_button(text, colors, emoji)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        # EXIT
        btn_exit = self.create_styled_button(
            "EXIT", 
            ["#7b1fa2", "#6a1b9a", "#4a148c"],
            "✖"
        )
        btn_exit.clicked.connect(self.exit_callback)
        layout.addWidget(btn_exit)

        self.setLayout(layout)

    def create_logo(self):
        """Logo without any stuff"""
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setContentsMargins(0, 0, 0, 0)
        
        logo_path = Path(__file__).parent.parent / "icone.ico"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(150, 150, 
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
                logo.setPixmap(pixmap)
        
        return logo

    def create_styled_button(self, text, colors, emoji):
        """Styled button"""
        btn = QPushButton(f"{emoji}  {text}")
        btn.setMinimumHeight(60)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[0]}, stop:1 {colors[1]});
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 15px;
                border: 2px solid {colors[2]};
                padding-left: 30px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[0]}dd, stop:1 {colors[1]}dd);
                border: 3px solid {colors[2]};
                font-size: 21px;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[1]}, stop:1 {colors[0]});
                padding-top: 2px;
            }}
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(3, 3)
        btn.setGraphicsEffect(shadow)
        
        return btn

    # Buttons functionalitu
    def open_simulator_menu(self):
        """Opens simulator's menu"""
        QMessageBox.information(self, "Simulator", 
                               "🏭 Simulator menu will be available soon!")

    def open_database_menu(self):
        """Opens DB Menu"""
        self.db_menu = DatabaseMenu(
            self.open_preview_callback,     # View Database
            self.edit_database,              # Edit Database
            self.run_checker,                 # Check Database
            self.show_main_menu                # Back to main
        )
        self.hide()
        self.db_menu.show()

    def open_settings(self):
        """Opens settings_launcher.py from settings"""
        settings_path = Path(__file__).parent.parent / "settings" / "settings_launcher.py"
        
        if not settings_path.exists():
            QMessageBox.warning(
                self, 
                "File Not Found", 
                f"settings_launcher.py not found at:\n{settings_path}"
            )
            return
            
        try:
            subprocess.Popen([sys.executable, str(settings_path)])
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Could not open Settings:\n{str(e)}"
            )

    def open_analytics(self):
        """Opens Analytics"""
        QMessageBox.information(self, "Analytics", 
                               "📊 Analytics will be available soon!")

    def open_user_guide(self):
        """Shows User Guide"""
        pdf_path = Path(__file__).parent.parent / "User Guide.docx"
        
        if not pdf_path.exists():
            QMessageBox.warning(
                self, 
                "File Not Found", 
                f"User Guide.pdf not found at:\n{pdf_path}"
            )
            return
            
        try:
            # For Windows
            import os
            os.startfile(str(pdf_path))
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Could not open User Guide:\n{str(e)}"
            )

    def open_users(self):
        """ Opens Users information""""
        QMessageBox.information(self, "Users", 
                               "👥 Users management will be available soon!")

    def edit_database(self):
        """Editor of DB"""
        QMessageBox.information(self, "Edit Database", 
                               "✏ Edit Database functionality will be added soon!")

    def run_checker(self):
        """Launches Checker.py""" #DOES NOT EXIST YET
        checker_path = Path(__file__).parent.parent / "Database" / "Checker" / "Checker.py"
        
        if not checker_path.exists():
            QMessageBox.warning(
                self, 
                "File Not Found", 
                f"Checker.py not found at:\n{checker_path}"
            )
            return
            
        try:
            subprocess.Popen([sys.executable, str(checker_path)])
            QMessageBox.information(
                self,
                "Checker Started",
                "💚 Database Checker has been started!"
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Could not run Checker.py:\n{str(e)}"
            )

    def show_main_menu(self):
        """Back to main menu"""
        if hasattr(self, 'db_menu'):
            self.db_menu.close()
        self.show()


# test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    def test_preview():
        print("Preview clicked")
        QMessageBox.information(None, "Preview", "View Database clicked!")
    
    def test_exit():
        print("Exit clicked")
        app.quit()
    
    window = MainMenu(test_preview, test_exit)
    window.show()
    sys.exit(app.exec())