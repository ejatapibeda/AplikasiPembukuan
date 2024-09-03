import webbrowser
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox, QDateEdit, QProgressBar, QDialogButtonBox, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QDate, QUrl
from PyQt5.QtGui import QDesktopServices, QDoubleValidator

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
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

class AddConsumerDialog(AddDialog):
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        setup_error_handling()
        self.setWindowTitle("Tambah/Edit Konsumen")
        if initial_data:
            self.load_data(initial_data)

    def setup_ui(self):
        self.name_input = QLineEdit()
        self.address_input = QLineEdit()
        self.sales_input = QLineEdit()
        self.job_input = QLineEdit()
        self.total_projects_input = QLineEdit()
        self.worker_input = QLineEdit()
        self.notes_input = QLineEdit()

        self.form_layout.addRow("Nama Konsumen:", self.name_input)
        self.form_layout.addRow("Alamat:", self.address_input)
        self.form_layout.addRow("Sales:", self.sales_input)
        self.form_layout.addRow("Pekerjaan:", self.job_input)
        self.form_layout.addRow("Total Proyek:", self.total_projects_input)
        self.form_layout.addRow("Tukang:", self.worker_input)
        self.form_layout.addRow("Keterangan:", self.notes_input)

        self.inputs = [
            self.name_input,
            self.address_input,
            self.sales_input,
            self.job_input,
            self.total_projects_input,
            self.worker_input,
            self.notes_input
        ]

    def load_data(self, data):
        self.name_input.setText(str(data[0]))
        self.address_input.setText(str(data[1]))
        self.sales_input.setText(str(data[2]))
        self.job_input.setText(str(data[3]))
        self.total_projects_input.setText(str(data[4]))
        self.worker_input.setText(str(data[5]))
        self.notes_input.setText(str(data[6]))

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
        
class AddTukangDialog(AddDialog):
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        setup_error_handling()
        self.setWindowTitle("Tambah/Edit Proyek Tukang")
        if initial_data:
            self.load_data(initial_data)

    def setup_ui(self):
        self.name_input = QLineEdit()
        self.address_input = QLineEdit()
        self.job_input = QLineEdit()
        self.size_input = QLineEdit()
        self.kb_input = QLineEdit()
        self.notes_input = QLineEdit()

        self.form_layout.addRow("Nama Konsumen:", self.name_input)
        self.form_layout.addRow("Alamat:", self.address_input)
        self.form_layout.addRow("Pekerjaan:", self.job_input)
        self.form_layout.addRow("Ukuran:", self.size_input)
        self.form_layout.addRow("KB:", self.kb_input)
        self.form_layout.addRow("Keterangan:", self.notes_input)

        self.inputs = [
            self.name_input,
            self.address_input,
            self.job_input,
            self.size_input,
            self.kb_input,
            self.notes_input
        ]

    def load_data(self, data):
        self.name_input.setText(data[0])
        self.address_input.setText(data[1])
        self.job_input.setText(data[2])
        self.size_input.setText(data[3])
        self.kb_input.setText(data[4])
        self.notes_input.setText(data[5])

    def get_data(self):
        return [
            self.name_input.text(),
            self.address_input.text(),
            self.job_input.text(),
            self.size_input.text(),
            self.kb_input.text(),
            self.notes_input.text()
        ]

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
            self.notes_input.text()
        ]

    def load_data(self, data):
        self.date_input.setDate(QDate.fromString(data[0], "dd/MM/yyyy"))
        self.item_input.setText(data[1])
        self.quantity_input.setText(data[2])
        self.unit_price_input.setText(data[3])
        self.total_label.setText(data[4])
        self.notes_input.setText(data[5])
        self.update_total()

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        setup_error_handling()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Authentication successful! You can close this window.')
        self.server.path = self.path

class BackupWorker(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, credentials):
        super().__init__()
        setup_error_handling()
        self.credentials = credentials

    def run(self):
        try:
            drive_service = build("drive", "v3", credentials=self.credentials)

            file_metadata = {"name": "project_management_backup.db"}
            media = MediaFileUpload("project_management.db", resumable=True)

            file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class AuthThread(QThread):
    auth_completed = pyqtSignal(object)
    auth_failed = pyqtSignal(str)

    def __init__(self, flow):
        super().__init__()
        self.flow = flow
        self.server = None
        self.is_cancelled = False

    def run(self):
        try:
            auth_url, _ = self.flow.authorization_url(prompt='consent')
            QDesktopServices.openUrl(QUrl(auth_url))
            
            self.server = HTTPServer(('localhost', 8080), RedirectHandler)
            self.server.timeout = 1  # Set a short timeout to allow frequent checks for cancellation
            
            while not self.is_cancelled:
                self.server.handle_request()
                if hasattr(self.server, 'path'):
                    break
            
            if self.is_cancelled:
                return
            
            authorization_response = urllib.parse.unquote(self.server.path)
            self.flow.fetch_token(authorization_response=authorization_response)
            
            self.auth_completed.emit(self.flow.credentials)
        except Exception as e:
            if not self.is_cancelled:
                self.auth_failed.emit(str(e))

    def cancel(self):
        self.is_cancelled = True
        if self.server:
            self.server.server_close()

class BackupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup ke Google Drive")
        self.setGeometry(200, 200, 400, 200)

        self.layout = QVBoxLayout(self)

        self.status_label = QLabel("Klik tombol di bawah untuk memulai backup", self)
        self.layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        self.auth_button = QPushButton("Mulai Backup", self)
        self.auth_button.clicked.connect(self.start_authentication)
        self.layout.addWidget(self.auth_button)

        self.flow = None
        self.credentials = None
        self.auth_thread = None
        self.backup_worker = None

    def start_authentication(self):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        with open('client_secret.json', 'r') as f:
            client_config = json.load(f)

        self.flow = Flow.from_client_config(
            client_config,
            scopes=['https://www.googleapis.com/auth/drive.file'],
            redirect_uri='http://localhost:8080/'
        )

        self.auth_thread = AuthThread(self.flow)
        self.auth_thread.auth_completed.connect(self.on_auth_completed)
        self.auth_thread.auth_failed.connect(self.on_auth_failed)
        self.auth_thread.start()

        self.status_label.setText("Browser akan terbuka. Silakan otorisasi aplikasi.")
        self.progress_bar.show()
        self.auth_button.setEnabled(False)

    def on_auth_completed(self, credentials):
        self.credentials = credentials
        self.save_credentials()
        self.status_label.setText("Autentikasi berhasil. Memulai backup...")
        self.start_backup()

    def on_auth_failed(self, error_message):
        self.progress_bar.hide()
        self.status_label.setText(f"Gagal melakukan autentikasi: {error_message}")
        self.auth_button.setEnabled(True)

    def start_backup(self):
        self.auth_button.setEnabled(False)
        self.progress_bar.show()

        self.backup_worker = BackupWorker(self.credentials)
        self.backup_worker.finished.connect(self.on_backup_finished)
        self.backup_worker.error.connect(self.on_backup_error)
        self.backup_worker.start()

    def on_backup_finished(self):
        self.progress_bar.hide()
        self.status_label.setText("Backup berhasil dilakukan.")
        self.auth_button.hide()  # Hide the button after successful backup

    def on_backup_error(self, error_message):
        self.progress_bar.hide()
        self.status_label.setText(f"Gagal melakukan backup: {error_message}")
        self.auth_button.setEnabled(True)

    def save_credentials(self):
        with open('token.json', 'w') as token:
            token.write(self.credentials.to_json())

    def closeEvent(self, event):
        if self.auth_thread and self.auth_thread.isRunning():
            reply = QMessageBox.question(self, 'Konfirmasi',
                                         "Proses autentikasi sedang berlangsung. Anda yakin ingin menutup?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.auth_thread.cancel()
                self.auth_thread.wait()  # Wait for the thread to finish
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def cleanup(self):
        if self.auth_thread:
            self.auth_thread.cancel()
            self.auth_thread.wait()
        if self.backup_worker:
            self.backup_worker.quit()
            self.backup_worker.wait()

class AddSalesProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah/Edit Proyek Sales")
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

        self.notes_edit = QLineEdit(self)
        form_layout.addRow("Keterangan:", self.notes_edit)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        return (
            self.customer_name_edit.text(),
            self.address_edit.text(),
            self.job_edit.text(),
            self.total_project_edit.text(),
            self.commission_edit.text(),
            self.kb_edit.text(),
            self.notes_edit.text()
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
        self.notes_edit.setText(str(data[6]))

class AddTukangProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah/Edit Proyek Tukang")
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

        self.notes_edit = QLineEdit(self)
        form_layout.addRow("Keterangan:", self.notes_edit)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        return (
            self.customer_name_edit.text(),
            self.address_edit.text(),
            self.job_edit.text(),
            self.size_edit.text(),
            self.kb_edit.text(),
            self.notes_edit.text()
        )

    def load_data(self, data):
        self.customer_name_edit.setText(str(data[0]))
        self.address_edit.setText(str(data[1]))
        self.job_edit.setText(str(data[2]))
        self.size_edit.setText(str(data[3]))
        self.kb_edit.setText(str(data[4]))
        self.notes_edit.setText(str(data[5]))
