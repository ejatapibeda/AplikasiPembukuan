import webbrowser
from PyQt5.QtWidgets import QDialog, QFileDialog, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QFormLayout, QComboBox, QDateEdit, QDialogButtonBox, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QDate, Qt
from PyQt5.QtGui import QGuiApplication, QDoubleValidator

import shutil
import os
from datetime import datetime
from error_handling import setup_error_handling



class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        setup_error_handling()
        self.setMinimumSize(600, 400) 
        self.setWindowTitle("Tambah Data")
        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.inputs = []
        self.setup_ui()
        self.layout.addLayout(self.form_layout)

        self.button_box = QVBoxLayout()
        self.submit_button = QPushButton("Simpan")
        self.submit_button.clicked.connect(self.accept)
        self.button_box.addWidget(self.submit_button)
        self.layout.addLayout(self.button_box)
        self.setLayout(self.layout)

    def setup_ui(self):
        pass

    def get_data(self):
        data = []
        for input_field in self.inputs:
            if isinstance(input_field, QLineEdit):
                data.append(input_field.text())
            elif isinstance(input_field, QComboBox):
                data.append(input_field.currentText())
            elif isinstance(input_field, QDateEdit):
                data.append(input_field.date().toString("dd/MM/yyyy"))
        return data

class AddConsumerDialog(QDialog):
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah/Edit Konsumen")
        self.setup_ui()
        if initial_data:
            self.load_data(initial_data)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Tanggal:", self.date_edit)

        self.name_input = QLineEdit(self)
        form_layout.addRow("Nama Konsumen:", self.name_input)

        self.address_input = QLineEdit(self)
        form_layout.addRow("Alamat:", self.address_input)

        self.sales_input = QLineEdit(self)
        form_layout.addRow("Sales:", self.sales_input)

        self.job_input = QLineEdit(self)
        form_layout.addRow("Pekerjaan:", self.job_input)

        self.total_projects_input = QLineEdit(self)
        form_layout.addRow("Total Proyek:", self.total_projects_input)

        self.worker_input = QLineEdit(self)
        form_layout.addRow("Tukang:", self.worker_input)

        self.notes_input = QTextEdit(self)
        self.notes_input.setMinimumHeight(100)
        form_layout.addRow("Keterangan:", self.notes_input)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        return [
            self.date_edit.date().toString("dd/MM/yyyy"),
            self.name_input.text(),
            self.address_input.text(),
            self.sales_input.text(),
            self.job_input.text(),
            self.total_projects_input.text(),
            self.worker_input.text(),
            self.notes_input.toPlainText()
        ]

    def load_data(self, data):
        print(data[5])
        self.date_edit.setDate(QDate.fromString(data[0], "dd/MM/yyyy"))
        self.name_input.setText(data[1])
        self.address_input.setText(data[2])
        self.sales_input.setText(data[3])
        self.job_input.setText(data[4])
        self.total_projects_input.setText(data[5])
        self.worker_input.setText(data[6])
        self.notes_input.setPlainText(data[7])

class ProjectInputDialog(QDialog):
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        self.setWindowTitle("Input Proyek Baru")
        self.layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit(self)
        form_layout.addRow("Nama Proyek:", self.name_input)
        
        self.sales_input = QLineEdit(self)
        form_layout.addRow("Nama Sales:", self.sales_input)
        
        self.worker_input = QLineEdit(self)
        form_layout.addRow("Nama Tukang:", self.worker_input)
        
        self.start_date_input = QDateEdit(self)
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        form_layout.addRow("Tanggal Mulai:", self.start_date_input)
        
        self.end_date_input = QDateEdit(self)
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        form_layout.addRow("Tanggal Selesai:", self.end_date_input)
        
        self.total_input = QLineEdit(self)
        self.total_input.setValidator(QDoubleValidator(0, 1e9, 2, self))
        form_layout.addRow("Total Proyek:", self.total_input)
        
        self.dp_input = QLineEdit(self)
        self.dp_input.setValidator(QDoubleValidator(0, 1e9, 2, self))
        form_layout.addRow("DP:", self.dp_input)
        
        self.layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)
        
        if initial_data:
            self.load_initial_data(initial_data)

    def load_initial_data(self, data):
        self.name_input.setText(data.get("Nama Proyek", ""))
        self.sales_input.setText(data.get("Nama Sales", ""))
        self.worker_input.setText(data.get("Nama Tukang", ""))
        self.start_date_input.setDate(QDate.fromString(data.get("Tanggal Mulai", ""), "dd/MM/yyyy"))
        self.end_date_input.setDate(QDate.fromString(data.get("Tanggal Selesai", ""), "dd/MM/yyyy"))
        
        # Format Total Proyek and DP as Rupiah for display
        total_proyek = self.parse_rupiah(data.get("Total Proyek", ""))
        self.total_input.setText(self.format_rupiah(total_proyek))
        
        dp = self.parse_rupiah(data.get("DP", ""))
        self.dp_input.setText(self.format_rupiah(dp))

    def get_project_data(self):
        return {
            "Nama Proyek": self.name_input.text(),
            "Nama Sales": self.sales_input.text(),
            "Nama Tukang": self.worker_input.text(),
            "Tanggal Mulai": self.start_date_input.date().toString("dd/MM/yyyy"),
            "Tanggal Selesai": self.end_date_input.date().toString("dd/MM/yyyy"),
            "Total Proyek": self.parse_rupiah(self.total_input.text()),
            "DP": self.parse_rupiah(self.dp_input.text())
        }

    def format_rupiah(self, value):
        try:
            numeric_value = float(value)
            return f"Rp {numeric_value:,.0f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except ValueError:
            return value

    def parse_rupiah(self, value):
        # Remove 'Rp ', replace thousand separator, and decimal separator
        return value.replace('Rp ', '').replace('.', '').replace(',', '.')

    def accept(self):
        # Validate inputs before accepting
        if not all([self.name_input.text(), self.sales_input.text(), self.worker_input.text(),
                    self.total_input.text(), self.dp_input.text()]):
            QMessageBox.warning(self, "Input Tidak Lengkap", "Harap isi semua field.")
            return
        
        super().accept()

class AddMaterialDialog(QDialog):
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        setup_error_handling()
        self.setMinimumSize(600, 400) 
        self.setWindowTitle("Tambah/Edit Pemakaian Bahan")
        self.layout = QVBoxLayout(self)
        self.setup_ui()
        if initial_data:
            self.load_data(initial_data)

    def setup_ui(self):
        self.form_layout = QFormLayout()

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.item_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.unit_price_input = QLineEdit()
        self.total_label = QLabel("0")
        self.notes_input = QLineEdit()

        self.form_layout.addRow("Tanggal:", self.date_input)
        self.form_layout.addRow("Nama Barang:", self.item_input)
        self.form_layout.addRow("Quantity:", self.quantity_input)
        self.form_layout.addRow("Harga Satuan:", self.unit_price_input)
        self.form_layout.addRow("Total:", self.total_label)
        self.notes_input = QTextEdit()
        self.notes_input.setMinimumHeight(100)
        self.form_layout.addRow("Keterangan:", self.notes_input)

        self.layout.addLayout(self.form_layout)

        self.button_box = QVBoxLayout()
        self.submit_button = QPushButton("Simpan")
        self.submit_button.clicked.connect(self.accept)
        self.button_box.addWidget(self.submit_button)
        self.layout.addLayout(self.button_box)

        # Connect signals to update total
        self.quantity_input.textChanged.connect(self.update_total)
        self.unit_price_input.textChanged.connect(self.update_total)

    def update_total(self):
        try:
            quantity = float(self.quantity_input.text() or 0)
            unit_price = float(self.unit_price_input.text() or 0)
            total = quantity * unit_price
            self.total_label.setText(f"{total:.2f}")
        except ValueError:
            self.total_label.setText("Invalid input")
    
    def validate_data(self):
        try:
            quantity = float(self.quantity_input.text())
            unit_price = float(self.unit_price_input.text())
            return True
        except ValueError:
            return False

    def get_data(self):
        return [
            self.date_input.date().toString("dd/MM/yyyy"),
            self.item_input.text(),
            self.quantity_input.text(),
            self.unit_price_input.text(),
            self.total_label.text(),
            self.notes_input.toPlainText()
        ]

    def load_data(self, data):
        self.date_input.setDate(QDate.fromString(data[0], "dd/MM/yyyy"))
        self.item_input.setText(data[1])
        self.quantity_input.setText(data[2])
        self.unit_price_input.setText(data[3])
        self.total_label.setText(data[4])
        self.notes_input.setPlainText(data[5])
        self.update_total()

class AddSalesProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah/Edit Proyek Sales")
        self.photo_path = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.customer_name_edit = QLineEdit(self)
        form_layout.addRow("Nama Konsumen:", self.customer_name_edit)

        self.address_edit = QLineEdit(self)
        form_layout.addRow("Alamat:", self.address_edit)

        self.job_edit = QLineEdit(self)
        form_layout.addRow("Pekerjaan:", self.job_edit)

        self.total_project_edit = QLineEdit(self)
        form_layout.addRow("Total Proyek:", self.total_project_edit)

        self.commission_edit = QLineEdit(self)
        form_layout.addRow("Komisi:", self.commission_edit)

        self.kb_edit = QLineEdit(self)
        form_layout.addRow("KB:", self.kb_edit)

        self.notes_edit = QTextEdit(self)
        self.notes_edit.setMinimumHeight(100)
        form_layout.addRow("Keterangan:", self.notes_edit)

        self.photo_button = QPushButton("Pilih Foto", self)
        self.photo_button.clicked.connect(self.choose_photo)
        form_layout.addRow("Foto:", self.photo_button)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def choose_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih Foto", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.photo_path = file_name
            self.photo_button.setText(os.path.basename(file_name))

    def get_photo_path(self):
        return self.photo_path

    def get_data(self):
        return (
            self.customer_name_edit.text(),
            self.address_edit.text(),
            self.job_edit.text(),
            self.total_project_edit.text(),
            self.commission_edit.text(),
            self.kb_edit.text(),
            self.notes_edit.toPlainText(),
        )
    
    def validate_data(self):
        try:
            float(self.total_project_edit.text().replace('Rp', '').replace('.', '').replace(',', '').strip())
            float(self.commission_edit.text().replace('Rp', '').replace('.', '').replace(',', '').strip())
            float(self.kb_edit.text().replace('Rp', '').replace('.', '').replace(',', '').strip())
            return True
        except ValueError:
            return False

    def load_data(self, data):
        self.customer_name_edit.setText(str(data[0]))
        self.address_edit.setText(str(data[1]))
        self.job_edit.setText(str(data[2]))
        self.total_project_edit.setText(str(data[3]))
        self.commission_edit.setText(str(data[4]))
        self.kb_edit.setText(str(data[5]))
        self.notes_edit.setPlainText(str(data[6]))

class AddTukangProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah/Edit Proyek Tukang")
        self.photo_path = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.customer_name_edit = QLineEdit(self)
        form_layout.addRow("Nama Konsumen:", self.customer_name_edit)

        self.address_edit = QLineEdit(self)
        form_layout.addRow("Alamat:", self.address_edit)

        self.job_edit = QLineEdit(self)
        form_layout.addRow("Pekerjaan:", self.job_edit)

        self.size_edit = QLineEdit(self)
        form_layout.addRow("Ukuran:", self.size_edit)

        self.kb_edit = QLineEdit(self)
        form_layout.addRow("KB:", self.kb_edit)

        self.notes_edit = QTextEdit(self)
        self.notes_edit.setMinimumHeight(100) 
        form_layout.addRow("Keterangan:", self.notes_edit)

        self.photo_button = QPushButton("Pilih Foto", self)
        self.photo_button.clicked.connect(self.choose_photo)
        form_layout.addRow("Foto:", self.photo_button)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def choose_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Pilih Foto", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.photo_path = file_name
            self.photo_button.setText(os.path.basename(file_name))

    def get_photo_path(self):
        return self.photo_path

    def get_data(self):
        return (
            self.customer_name_edit.text(),
            self.address_edit.text(),
            self.job_edit.text(),
            self.size_edit.text(),
            self.kb_edit.text(),
            self.notes_edit.toPlainText()
        )

    def load_data(self, data):
        self.customer_name_edit.setText(str(data[0]))
        self.address_edit.setText(str(data[1]))
        self.job_edit.setText(str(data[2]))
        self.size_edit.setText(str(data[3]))
        self.kb_edit.setText(str(data[4]))
        self.notes_edit.setPlainText(str(data[5]))

class BackupWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, source_path, destination_path):
        super().__init__()
        self.source_path = source_path
        self.destination_path = destination_path

    def run(self):
        try:
            os.makedirs(os.path.dirname(self.destination_path), exist_ok=True)
            shutil.copy2(self.source_path, self.destination_path)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class BackupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup Database")
        self.setFixedSize(1, 1)  # Minimal size to make the dialog invisible
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove window decorations

        # Start the backup process immediately
        self.confirm_backup()

    def center_message_box(self, message_box):
        message_box.show()
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        center_point = screen_geometry.center()
        message_box_geometry = message_box.frameGeometry()
        message_box_geometry.moveCenter(center_point)
        message_box.move(message_box_geometry.topLeft())
    
    def confirm_backup(self):
        current_date = datetime.now().strftime("%d %B %Y")
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('Konfirmasi Backup')
        msg_box.setText(f"Apakah Anda yakin ingin melakukan backup pada tanggal {current_date}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        self.center_message_box(msg_box)
        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            self.start_backup()
        else:
            self.reject()  # Close the dialog if user selects No

    def start_backup(self):
        current_date = datetime.now().strftime("%d-%m-%Y")
        backup_folder = os.path.join("backup", current_date)
        
        source_path = "project_management.db"
        destination_path = os.path.join(backup_folder, "project_management.db")

        # Check if a backup already exists for today
        counter = 1
        while os.path.exists(destination_path):
            counter += 1
            destination_path = os.path.join(backup_folder, f"project_management({counter}).db")

        self.backup_worker = BackupWorker(source_path, destination_path)
        self.backup_worker.finished.connect(self.on_backup_finished)
        self.backup_worker.error.connect(self.on_backup_error)
        self.backup_worker.start()

    def on_backup_finished(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Backup Berhasil")
        msg_box.setText("Database berhasil di-backup ke folder lokal.")
        self.center_message_box(msg_box)
        msg_box.exec_()
        self.accept()  # Close the dialog

    def on_backup_error(self, error_message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Backup Gagal")
        msg_box.setText(f"Gagal melakukan backup: {error_message}")
        self.center_message_box(msg_box)
        msg_box.exec_()
        self.reject()  # Close the dialog

    def closeEvent(self, event):
        if hasattr(self, 'backup_worker') and self.backup_worker.isRunning():
            self.backup_worker.quit()
            self.backup_worker.wait()
        event.accept()