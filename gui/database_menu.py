import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, 
    QApplication, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from PyQt6.QtGui import QIcon
from pathlib import Path


class DatabaseMenu(QWidget):
    def __init__(self, view_callback, edit_callback, check_callback, back_callback):
        super().__init__()
        self.view_callback = view_callback
        self.edit_callback = edit_callback
        self.check_callback = check_callback
        self.back_callback = back_callback
        
        self.setWindowTitle("🗄 Database Menu")
        self.setFixedSize(500, 500)
        
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
        layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = self.create_title("🗄 Database Menu")
        layout.addWidget(title)

        # Menu buttons
        buttons_info = [
            ("👁 View Database", self.view_callback, 
             ["#FF00CC", "#FF00CC", "#FF00CC"]),
            ("✏ Edit Database", self.edit_callback,
             ["#C3009C", "#C3009C", "#C3009C"]),
            ("💚 Check Database", self.check_callback,
             ["#930076", "#930076", "#930076"]),
            ("🔙 Back to Main Menu", self.back_callback,
             ["#FF0000", "#FF0000", "#FF0000"]),
        ]

        for text, callback, colors in buttons_info:
            btn = self.create_styled_button(text, colors)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        self.setLayout(layout)

    def create_title(self, text):
        """Styled title"""
        title = QLabel(text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6a1b9a, stop:0.5 #2e7d32, stop:1 #1565c0);
                border-radius: 15px;
                border: 2px solid rgba(255, 255, 255, 0.2);
                margin-bottom: 20px;
            }
        """)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(3, 3)
        title.setGraphicsEffect(shadow)
        
        return title

    def create_styled_button(self, text, colors):
        """Styled buttons with a gradient"""
        btn = QPushButton(text)
        btn.setMinimumHeight(60)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[0]}, stop:1 {colors[1]});
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
                border: 2px solid {colors[2]};
                padding-left: 20px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[0]}dd, stop:1 {colors[1]}dd);
                border: 3px solid {colors[2]};
                font-size: 19px;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors[1]}, stop:1 {colors[0]});
                padding-top: 2px;
                padding-left: 22px;
            }}
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(Qt.GlobalColor.black)
        shadow.setOffset(2, 2)
        btn.setGraphicsEffect(shadow)
        
        return btn



if __name__ == "__main__":
    app = QApplication(sys.argv)
 
    def test_view():
        print("View clicked")
        
    def test_edit():
        print("Edit clicked")
        
    def test_check():
        print("Check clicked")
        
    def test_back():
        print("Back clicked")
        window.close()
    
    window = DatabaseMenu(test_view, test_edit, test_check, test_back)
    window.show()
    sys.exit(app.exec())