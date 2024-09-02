from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QVBoxLayout, QLabel, QStackedWidget, QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize
from dialogs import BackupDialog
from table_views import ConsumerTable, SalesTable, TukangTable, MaterialTable
from modern_button import ModernButton
from error_handling import setup_error_handling
import os
import subprocess
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        setup_error_handling()
        self.setWindowTitle("Manajemen Proyek")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('image/icon.png'))

        self.main_layout = QHBoxLayout()
        
        self.setup_sidebar()
        self.setup_main_area()
        
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
        
        self.dark_mode = False
        self.toggle_theme()

        self.user_id = None

    def set_user_id(self, user_id):
        self.user_id = user_id
        self.consumer_table.set_user_id(user_id)
        self.sales_table.set_user_id(user_id)
        self.tukang_table.set_user_id(user_id)
        self.material_table.set_user_id(user_id)

    def refresh_tables(self):
        self.consumer_table.set_user_id(self.user_id)
        self.sales_table.set_user_id(self.user_id)
        self.tukang_table.set_user_id(self.user_id)
        self.material_table.set_user_id(self.user_id)

    def show_fullscreen(self):
        self.showMaximized()

    def setup_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(250)
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)

        self.logo_label = QLabel("Project Manager")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0;")
        self.sidebar_layout.addWidget(self.logo_label)

        self.add_sidebar_button("Daftar Konsumen", 0, "user")
        self.add_sidebar_button("Daftar Proyek Sales", 1, "briefcase")
        self.add_sidebar_button("Daftar Proyek Tukang", 2, "tools")
        self.add_sidebar_button("Daftar Pemakaian Bahan", 3, "box")

        self.sidebar_layout.addStretch()
        
        self.update_button = ModernButton("Check for Updates", "refresh")
        self.update_button.clicked.connect(self.check_for_updates)
        self.sidebar_layout.addWidget(self.update_button)

        self.backup_button = ModernButton("Backup ke Google Drive", "cloud-upload")
        self.backup_button.clicked.connect(self.open_backup_dialog)
        self.sidebar_layout.addWidget(self.backup_button)

        self.toggle_theme_btn = ModernButton("Toggle Dark/Light Mode", "adjust")
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        self.sidebar_layout.addWidget(self.toggle_theme_btn)

        self.main_layout.addWidget(self.sidebar)

    def setup_main_area(self):
        self.stack = QStackedWidget()
        self.consumer_table = ConsumerTable(self)
        self.sales_table = SalesTable(self)
        self.tukang_table = TukangTable(self)
        self.material_table = MaterialTable(self)

        self.stack.addWidget(self.consumer_table)
        self.stack.addWidget(self.sales_table)
        self.stack.addWidget(self.tukang_table)
        self.stack.addWidget(self.material_table)

        self.main_layout.addWidget(self.stack)

    def add_sidebar_button(self, name, index, icon):
        btn = ModernButton(name, icon)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        self.sidebar_layout.addWidget(btn)

    def toggle_theme(self):
        if self.dark_mode:
            self.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #f0f0f0;
            color: #333333;
        }
        QTableWidget {
            gridline-color: #cccccc;
            background-color: white;
            alternate-background-color: #e6e6e6;
        }
        QTableWidget::item {
            color: #333333;
        }
        QHeaderView::section {
            background-color: #d9d9d9;
            color: #333333;
            padding: 5px;
            border: 1px solid #cccccc;
        }
        QLineEdit, QDateEdit {
            background-color: white;
            color: #333333;
            border: 1px solid #cccccc;
            padding: 5px;
            border-radius: 4px;
        }
        QGroupBox {
            border: 1px solid #cccccc;
            margin-top: 10px;
            border-radius: 4px;
        }
        QGroupBox::title {
            color: #333333;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        """)
        else:
            self.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #2c3e50;
            color: #ecf0f1;
        }
        QTableWidget {
            gridline-color: #34495e;
            background-color: #2c3e50;
            alternate-background-color: #34495e;
        }
        QTableWidget::item {
            color: #ecf0f1;
        }
        QHeaderView::section {
            background-color: #34495e;
            color: #ecf0f1;
            padding: 5px;
            border: 1px solid #2c3e50;
        }
        QLineEdit, QDateEdit {
            background-color: #34495e;
            color: #ecf0f1;
            border: 1px solid #2c3e50;
            padding: 5px;
            border-radius: 4px;
        }
        QGroupBox {
            border: 1px solid #34495e;
            margin-top: 10px;
            border-radius: 4px;
        }
        QGroupBox::title {
            color: #ecf0f1;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        """)
        self.dark_mode = not self.dark_mode

    def open_backup_dialog(self):
        dialog = BackupDialog(self)
        dialog.exec_()
    
    def check_for_updates(self):
        update_exe = 'update.exe'
        if os.path.exists(update_exe):
            try:
                # Jalankan update.exe dan tangkap outputnya
                result = subprocess.run([update_exe], capture_output=True, text=True, timeout=30)
                
                if "Update tersedia" in result.stdout:
                    version = result.stdout.split(":")[-1].strip()
                    reply = QMessageBox.question(self, 'Update Tersedia', 
                                                 f"Update versi {version} tersedia. Apakah Anda ingin menginstal?",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.install_update()
                else:
                    QMessageBox.information(self, "Update", "Tidak ada update tersedia.")
            except subprocess.TimeoutExpired:
                QMessageBox.warning(self, "Update", "Timeout saat memeriksa update.")
            except Exception as e:
                QMessageBox.warning(self, "Update", f"Error saat memeriksa update: {str(e)}")
        else:
            QMessageBox.warning(self, "Update", "File update.exe tidak ditemukan.")

    def install_update(self):
        update_exe = 'update.exe'
        try:
            self.close()  # Tutup aplikasi utama
            subprocess.Popen([update_exe, "--install"])  # Jalankan updater untuk instalasi
            sys.exit()  # Keluar dari aplikasi utama
        except Exception as e:
            QMessageBox.critical(self, "Update Error", f"Gagal menginstal update: {str(e)}")