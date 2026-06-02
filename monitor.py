import requests
import json
import time
import schedule
from datetime import datetime, timedelta
import logging

TELEGRAM_TOKEN = "7535762489:AAHzzcXt5PxNZ4vpbVuiFb3CYvmErWcD8m4"
CHAT_ID = "5271405408"
CHECK_INTERVAL = 15
MONITOR_WINDOW_MINUTES = 60

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
sent_signals = set()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}, timeout=10)
        log.info("Сообщение отправлено")
    except Exception as e:
        log.error(f"Ошибка: {e}")

def run_checks():
    log.info(f"Проверка {datetime.now().strftime('%H:%M')}")
    send_telegram(f"✅ Проверка запущена {datetime.now().strftime('%H:%M')}")

def main():
    send_telegram("🚀 <b>Betting Monitor запущен!</b>")
    run_checks()
    schedule.every(CHECK_INTERVAL).minutes.do(run_checks)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
