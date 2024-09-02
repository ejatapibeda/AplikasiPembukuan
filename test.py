import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QTabWidget,
                             QLabel, QHeaderView, QStyle, QSizePolicy)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt

class ProjectManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Manager")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
                border-radius: 5px;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #f6f7fa, stop: 1 #dadbde);
                border: 1px solid #C4C4C3;
                border-bottom-color: #C2C7CB;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 8px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                            stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
            }
            QTabBar::tab:selected {
                border-color: #9B9B9B;
                border-bottom-color: #C2C7CB;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTableWidget {
                gridline-color: #ddd;
                selection-background-color: #a6a6a6;
            }
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        # Membuat widget utama dan layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Membuat tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Tab Daftar Konsumen
        konsumen_widget = QWidget()
        konsumen_layout = QVBoxLayout(konsumen_widget)
        tab_widget.addTab(konsumen_widget, "Daftar Konsumen")
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Cari:")
        search_label.setFont(QFont("Arial", 12))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari konsumen...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        konsumen_layout.addLayout(search_layout)
        
        # Tabel Konsumen
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Nama Konsumen", "Alamat", "Sales", "Pekerjaan", "Total Proyek", "Tukang", "Keterangan"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        konsumen_layout.addWidget(self.table)
        
        # Data dummy
        self.konsumen_data = [
            ["PT Maju Jaya", "Jl. Raya No. 123, Jakarta", "Budi", "Konstruksi", "5", "Ahmad", "Proyek berjalan lancar"],
            ["CV Sukses Abadi", "Jl. Gatot Subroto No. 45, Bandung", "Siti", "Renovasi", "3", "Rudi", "Menunggu bahan baku"],
            ["Toko Makmur", "Jl. Pahlawan No. 78, Surabaya", "Dedi", "Interior", "2", "Joko", "Selesai minggu depan"],
            ["PT Karya Indah", "Jl. Diponegoro No. 56, Semarang", "Rina", "Eksterior", "4", "Agus", "Dalam proses pengerjaan"]
        ]
        self.populate_table()
        
        # Tombol-tombol aksi
        button_layout = QHBoxLayout()
        buttons = [
            ("Tambah", self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)),
            ("Edit", self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogStart)),
            ("Hapus", self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)),
            ("Export to Excel", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)),
            ("Lihat Riwayat", self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)),
            ("Tutup Buku", self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
        ]
        for button_text, icon in buttons:
            button = QPushButton(icon, button_text)
            button.clicked.connect(lambda _, text=button_text: self.button_clicked(text))
            button_layout.addWidget(button)
        konsumen_layout.addLayout(button_layout)
        
        # Tombol Backup
        backup_button = QPushButton(self.style().standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon), "Backup ke Google Drive")
        backup_button.clicked.connect(lambda: self.button_clicked("Backup"))
        backup_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        konsumen_layout.addWidget(backup_button)
        
        # Tab lainnya (placeholder)
        tab_widget.addTab(QWidget(), "Daftar Proyek Sales")
        tab_widget.addTab(QWidget(), "Daftar Proyek Tukang")
        tab_widget.addTab(QWidget(), "Daftar Pemakaian Bahan")
        
    def populate_table(self):
        self.table.setRowCount(len(self.konsumen_data))
        for row, konsumen in enumerate(self.konsumen_data):
            for col, value in enumerate(konsumen):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)
    
    def filter_table(self):
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
    def button_clicked(self, button_text):
        print(f"Tombol {button_text} diklik")
        # Implementasi fungsi tombol akan ditambahkan di sini

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProjectManager()
    window.show()
    sys.exit(app.exec())