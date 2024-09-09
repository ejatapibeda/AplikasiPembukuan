from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QDesktopWidget, QLineEdit, QPushButton, 
                             QLabel, QStackedWidget, QMessageBox, QFrame)
from PyQt5.QtGui import QColor, QPalette, QFont, QIcon
from PyQt5.QtCore import Qt, QSize
from auth import Auth

class ModernDarkPalette(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.Window, QColor(71, 71, 71))
        self.setColor(QPalette.WindowText, Qt.white)
        self.setColor(QPalette.Base, QColor(25, 25, 25))
        self.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.setColor(QPalette.ToolTipBase, Qt.white)
        self.setColor(QPalette.ToolTipText, Qt.white)
        self.setColor(QPalette.Text, Qt.white)
        self.setColor(QPalette.Button, QColor(53, 53, 53))
        self.setColor(QPalette.ButtonText, Qt.white)
        self.setColor(QPalette.BrightText, Qt.red)
        self.setColor(QPalette.Link, QColor(42, 130, 218))
        self.setColor(QPalette.Highlight, QColor(42, 130, 218))
        self.setColor(QPalette.HighlightedText, Qt.black)

class StyleHelper:
    @staticmethod
    def get_line_edit_style():
        return """
        QLineEdit {
            border: none;
            border-bottom: 2px solid #3498db;
            padding: 8px;
            margin-bottom: 15px;
            background-color: transparent;
            color: white;
            font-size: 18px;
        }
        QLineEdit:focus {
            border-bottom: 2px solid #2980b9;
        }
        """

    @staticmethod
    def get_button_style():
        return """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px;
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
        """

    @staticmethod
    def get_link_style():
        return """
        QLabel {
            color: #3498db;
            font-size: 16px;
        }
        QLabel:hover {
            color: #2980b9;
        }
        """

class AuthWidget(QWidget):
    def __init__(self, stacked_widget, auth, main_window, is_login=True):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.auth = auth
        self.main_window = main_window
        self.is_login = is_login
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Set up title
        title = QLabel("Login" if self.is_login else "Register")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 30px; color: white;")
        layout.addWidget(title)

        # Set up input fields
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet(StyleHelper.get_line_edit_style())
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(StyleHelper.get_line_edit_style())
        layout.addWidget(self.password_input)

        if not self.is_login:
            self.confirm_password_input = QLineEdit()
            self.confirm_password_input.setPlaceholderText("Confirm Password")
            self.confirm_password_input.setEchoMode(QLineEdit.Password)
            self.confirm_password_input.setStyleSheet(StyleHelper.get_line_edit_style())
            layout.addWidget(self.confirm_password_input)

        # Set up action button
        action_button = QPushButton("Login" if self.is_login else "Register")
        action_button.setStyleSheet(StyleHelper.get_button_style())
        action_button.clicked.connect(self.login if self.is_login else self.register)
        layout.addWidget(action_button)

        # Set up switch view link
        switch_text = "Don't have an account? Register" if self.is_login else "Already have an account? Login"
        switch_link = QLabel(switch_text)
        switch_link.setStyleSheet(StyleHelper.get_link_style())
        switch_link.setAlignment(Qt.AlignCenter)
        switch_link.mousePressEvent = self.switch_view
        layout.addWidget(switch_link)

        layout.addStretch()
        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        user_id = self.auth.login(username, password)
        if user_id:
            self.main_window.set_user_id(user_id)
            self.main_window.show_fullscreen()
            self.window().close()
        else:
            QMessageBox.warning(self, 'Login Failed', 'Invalid username or password')

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if password != confirm_password:
            QMessageBox.warning(self, 'Registration Failed', 'Passwords do not match')
            return

        if self.auth.register(username, password):
            QMessageBox.information(self, 'Registration Successful', 'You can now login with your new account')
            self.switch_view(None)
        else:
            QMessageBox.warning(self, 'Registration Failed', 'Username already exists')

    def switch_view(self, event):
        self.stacked_widget.setCurrentIndex(1 if self.is_login else 0)

class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.auth = Auth()
        self.main_window = main_window
        self.init_ui()
        self.center_on_screen()

    def init_ui(self):
        self.setWindowTitle('Aplikasi Pembukuan Proyek')
        self.setFixedSize(600, 800)  # Increased window size
        self.setWindowIcon(QIcon('image/icon.png'))
        
        main_layout = QVBoxLayout()
        
        # Set up logo
        logo_label = QLabel("Aplikasi Pembukuan Proyek")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            margin: 30px 0;
            color: white;
            padding: 15px;
            border-radius: 8px;
        """)
        main_layout.addWidget(logo_label)
        
        # Set up main frame
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 15px;
                padding: 30px;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        
        # Set up stacked widget for login and register views
        self.stacked_widget = QStackedWidget()
        login_widget = AuthWidget(self.stacked_widget, self.auth, self.main_window, is_login=True)
        register_widget = AuthWidget(self.stacked_widget, self.auth, self.main_window, is_login=False)
        self.stacked_widget.addWidget(login_widget)
        self.stacked_widget.addWidget(register_widget)
        frame_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(frame)
        self.setLayout(main_layout)
        
        self.setPalette(ModernDarkPalette())

    def center_on_screen(self):
        # Get the screen geometry
        screen = QDesktopWidget().screenNumber(QDesktopWidget().cursor().pos())
        center_point = QDesktopWidget().screenGeometry(screen).center()
        
        # Move the window to the center
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())