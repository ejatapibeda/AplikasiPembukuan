import json
import os
import sys
import requests
import subprocess
import argparse

CONFIG_FILE = 'config.json'
GITHUB_REPO = 'username/repo'  # Ganti dengan username dan repo Anda

def get_current_version():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config['version']

def get_latest_version():
    url = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'
    response = requests.get(url)
    response.raise_for_status()  # Akan menimbulkan exception jika permintaan gagal
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
        install_update()
    else:
        check_for_updates()

def check_for_updates():
    current_version = get_current_version()
    latest_version = get_latest_version()
    
    if current_version != latest_version:
        print(f"Update tersedia: {latest_version}")
    else:
        print("Tidak ada update tersedia")

def install_update():
    latest_version = get_latest_version()
    new_exe = download_update(latest_version)
    
    if new_exe:
        print(f"Berhasil mengunduh {new_exe}")
        update_config(latest_version)
        print("Config.json telah diperbarui")
        
        # Ganti aplikasi lama dengan yang baru
        os.rename(sys.executable, f"{sys.executable}.old")
        os.rename(new_exe, sys.executable)
        
        print("Update selesai. Memulai ulang aplikasi...")
        subprocess.Popen([sys.executable])
    else:
        print("Gagal mengunduh update")

if __name__ == "__main__":
    main()
