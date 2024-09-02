import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from main_window import MainWindow
from login_window import LoginWindow
from error_handling import setup_error_handling

def set_app_style(app):
    app.setStyle("Fusion")
    font = QFont("Arial", 10)
    app.setFont(font)

if __name__ == "__main__":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

    app = QApplication(sys.argv)
    setup_error_handling()
    set_app_style(app)
    
    main_window = MainWindow()
    login_window = LoginWindow(main_window)
    login_window.show()
    
    sys.exit(app.exec_())