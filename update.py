import json
import os
import sys
import requests
import subprocess
import argparse
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QLabel, QMessageBox, QDesktopWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal

CONFIG_FILE = 'config.json'
GITHUB_REPO = 'ejatapibeda/AplikasiPembukuan'
LOG_FILE = 'update_log.txt'

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class UpdaterThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)  # Pass the filename

    def run(self):
        try:
            logging.info("Memulai proses update.")
            self.status_signal.emit("Memeriksa versi terbaru...")
            latest_version = get_latest_version()
            self.progress_signal.emit(20)

            self.status_signal.emit("Mengunduh update... Mohon Tunggu")
            logging.info(f"Versi terbaru yang ditemukan: {latest_version}")
            new_exe = download_update(latest_version)
            if not new_exe:
                raise Exception("Gagal mengunduh update")
            self.progress_signal.emit(60)

            self.status_signal.emit("Memperbarui konfigurasi...")
            update_config(latest_version)
            self.progress_signal.emit(100)

            self.status_signal.emit("Update selesai")
            logging.info("Update berhasil.")
            self.finished_signal.emit(True, new_exe)  # Pass the filename
        except Exception as e:
            logging.error(f"Error saat update: {str(e)}")
            self.status_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False, "")

class UpdaterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.status_label = QLabel("Memulai proses update...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle('Update Installer')
        self.resize(400, 150)
        self.center()  # Center the window
        self.setStyleSheet("""
        QWidget {
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QLabel {
            font-size: 14px;
            color: #333;
            margin-bottom: 10px;
        }
        QProgressBar {
            border: none;
            background-color: #e0e0e0;
            height: 8px;
            border-radius: 4px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 4px;
        }
        """)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def start_update(self):
        self.thread = UpdaterThread()
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.status_signal.connect(self.update_status)
        self.thread.finished_signal.connect(self.update_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(status)

    def update_finished(self, success, filename):
        if success:
            reply = QMessageBox.question(self, 'Update Berhasil',
                                     "Update selesai. Apakah Anda ingin membuka aplikasi sekarang?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                subprocess.Popen([filename])  # Open the downloaded file
            QApplication.instance().quit()
        else:
            logging.error("Update gagal.")
            QMessageBox.critical(self, 'Update Gagal', "Update gagal. Silakan coba lagi nanti.")
            QApplication.instance().quit()


def get_current_version():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    logging.info(f"Versi saat ini: {config['version']}")
    return config['version']

def get_latest_version():
    url = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'
    response = requests.get(url)
    response.raise_for_status()
    latest_release = response.json()
    return latest_release['tag_name']

def download_update(version):
    url = f'https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{version}'
    response = requests.get(url)
    response.raise_for_status()
    release = response.json()

    for asset in release['assets']:
        if asset['name'].endswith('.exe'):
            download_url = asset['browser_download_url']
            response = requests.get(download_url)
            with open(asset['name'], 'wb') as f:
                f.write(response.content)
            logging.info(f"File update {asset['name']} berhasil diunduh.")
            return asset['name']
    
    logging.warning("Tidak ada file update yang ditemukan.")
    return None

def update_config(new_version):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    config['version'] = new_version
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    
    logging.info(f"Konfigurasi diperbarui ke versi {new_version}.")

def main():
    parser = argparse.ArgumentParser(description="Update checker and installer")
    parser.add_argument("--install", action="store_true", help="Install update")
    args = parser.parse_args()

    if args.install:
        app = QApplication(sys.argv)
        gui = UpdaterGUI()
        gui.show()
        gui.start_update()
        sys.exit(app.exec_())
    else:
        check_for_updates()

def check_for_updates():
    current_version = get_current_version()
    latest_version = get_latest_version()
    
    if current_version != latest_version:
        print(f"Update tersedia: {latest_version}")
        logging.info(f"Update tersedia: {latest_version}")
    else:
        print("Tidak ada update tersedia")
        logging.info("Tidak ada update tersedia")

if __name__ == "__main__":
    main()
