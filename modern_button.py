from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from error_handling import setup_error_handling

class ModernButton(QPushButton):
    def __init__(self, text, icon_name=None, parent=None):
        super().__init__(text, parent)
        setup_error_handling()
        self.setFont(QFont("Arial", 10))
        self.setCursor(Qt.PointingHandCursor)
        
        if icon_name:
            icon = QIcon(f"image/{icon_name}.png")  # Assuming you have icon files in an 'icons' folder
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                text-align: left;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)