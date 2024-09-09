import sys
import traceback
import logging
from datetime import datetime
import requests
import os
from PyQt5.QtWidgets import QMessageBox

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1277660263931318322/jvc5PSJ763Zyohkd5PBQrfyhKouzCnMRsllBL-WUqE6AvVV-2dk7aDoGS7QDvi7qZ8zV"

def setup_error_handling():
    logging.basicConfig(filename='log.txt', level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    def handle_exception(exc_type, exc_value, exc_traceback):
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        error_msg = f"An unexpected error occurred:\n{exc_value}"
        error_box = QMessageBox(QMessageBox.Critical, "Error", error_msg)
        error_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Help)
        button = error_box.exec_()

        if button == QMessageBox.Help:
            send_to_discord(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception

def send_to_discord(exc_type, exc_value, exc_traceback):
    if not DISCORD_WEBHOOK_URL:
        QMessageBox.warning(None, "Error", "Discord webhook URL is not set in the environment variables.")
        return
    
    error_message = f"```\nType: {exc_type}\nValue: {exc_value}\n\nTraceback:\n{''.join(traceback.format_tb(exc_traceback))}```"
    payload = {
        "content": "An error occurred in the application:",
        "embeds": [{
            "title": "Error Details",
            "description": error_message,
            "color": 16711680  # Red color
        }]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        QMessageBox.information(None, "Success", "Error report sent to Discord successfully.")
    except requests.RequestException as e:
        QMessageBox.warning(None, "Error", f"Failed to send error report to Discord: {str(e)}")

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
            error_box = QMessageBox(QMessageBox.Warning, "Error", f"An error occurred in {func.__name__}: {str(e)}")
            error_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Help)
            button = error_box.exec_()

            if button == QMessageBox.Help:
                send_to_discord(type(e), str(e), e.__traceback__)
    return wrapper