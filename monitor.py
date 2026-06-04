import requests
import time
import schedule
from datetime import datetime
import logging

TELEGRAM_TOKEN = "7535762489:AAHzzcXt5PxNZ4vpbVuiFb3CYvmErWcD8m4"
CHAT_ID = "5271405408"
CHECK_INTERVAL = 15

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
sent_signals = set()

def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        log.error(f"Ошибка: {e}")

def check_nbbet():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://nb-bet.com/ru/football", headers=headers, timeout=15)
        log.info(f"NB-Bet статус: {r.status_code}")
        send_telegram(f"✅ NB-Bet проверен {datetime.now().strftime('%H:%M')}")
    except Exception as e:
        log.error(f"NB-Bet ошибка: {e}")

def run_checks():
    log.info(f"Проверка {datetime.now().strftime('%H:%M')}")
    check_nbbet()

def main():
    send_telegram("🚀 <b>Betting Monitor запущен!</b>")
    run_checks()
    schedule.every(CHECK_INTERVAL).minutes.do(run_checks)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
