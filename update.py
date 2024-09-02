import json
import os
import sys
import requests
import subprocess
import argparse
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal

CONFIG_FILE = 'config.json'
GITHUB_REPO = 'ejatapibeda/AplikasiPembukuan'

class UpdaterThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def run(self):
        try:
            self.status_signal.emit("Memeriksa versi terbaru...")
            latest_version = get_latest_version()
            self.progress_signal.emit(10)

            self.status_signal.emit("Mengunduh update...")
            new_exe = download_update(latest_version)
            if not new_exe:
                raise Exception("Gagal mengunduh update")
            self.progress_signal.emit(50)

            self.status_signal.emit("Memperbarui konfigurasi...")
            update_config(latest_version)
            self.progress_signal.emit(60)

            self.status_signal.emit("Mengganti file aplikasi...")
            old_executable = sys.executable
            new_executable_name = os.path.basename(old_executable)
            os.remove(old_executable)
            os.rename(new_exe, new_executable_name)
            self.progress_signal.emit(90)

            self.status_signal.emit("Memulai ulang aplikasi...")
            subprocess.Popen([new_executable_name])
            self.progress_signal.emit(100)
            
            self.finished_signal.emit(True)
        except Exception as e:
            self.status_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False)

class UpdaterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.status_label = QLabel("Memulai proses update...")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle('Update Installer')
        self.setGeometry(300, 300, 400, 150)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QProgressBar {
                border: 2px solid #bcbcbc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
                margin: 0.5px;
            }
        """)

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

    def update_finished(self, success):
        if success:
            self.status_label.setText("Update selesai. Aplikasi akan dimulai ulang.")
        else:
            self.status_label.setText("Update gagal. Silakan coba lagi nanti.")
        QApplication.instance().quit()

def get_current_version():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
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
            return asset['name']
    
    return None

def update_config(new_version):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    config['version'] = new_version
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

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
    else:
        print("Tidak ada update tersedia")

if __name__ == "__main__":
    main()