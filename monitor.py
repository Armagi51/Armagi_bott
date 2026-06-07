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

def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        log.error(f"Ошибка: {e}")

def get_matches():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "*/*",
            "Accept-Language": "ru,en;q=0.9",
            "Origin": "https://www.flashscore.com",
            "Referer": "https://www.flashscore.com/football/",
        }
        r = requests.get(
            "https://d.flashscore.com/x/feed/f_1_0_1_ru_1",
            headers=headers,
            timeout=15
        )
        log.info(f"Статус: {r.status_code}, размер: {len(r.text)}")
        send_telegram(
            f"✅ Flashscore API\n"
            f"Статус: {r.status_code}\n"
            f"Размер: {len(r.text)} байт\n"
            f"Первые 500 символов:\n{r.text[:500]}"
        )
    except Exception as e:
        send_telegram(f"❌ Ошибка: {e}")

def run_checks():
    get_matches()

def main():
    send_telegram("🔍 <b>Тест Flashscore API v3...</b>")
    run_checks()
    schedule.every(CHECK_INTERVAL).minutes.do(run_checks)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
