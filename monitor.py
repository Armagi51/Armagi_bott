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
odds_history = {}

def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        log.error(f"Ошибка: {e}")

def get_flashscore_odds(match_id):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "x-fsign": "SW9D1eZo"
        }
        r = requests.get(
            f"https://2.fn.sportradar.com/common/en/Etc:UTC/gismo/match_info/{match_id}",
            headers=headers, timeout=10
        )
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        log.error(f"Ошибка: {e}")
    return None

def get_matches():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "x-fsign": "SW9D1eZo"
        }
        r = requests.get(
            "https://d.flashscore.com/x/feed/f_1_0_1_ru_1",
            headers=headers, timeout=15
        )
        log.info(f"Flashscore статус: {r.status_code}, размер: {len(r.text)}")
        if r.status_code == 200:
            send_telegram(f"✅ Flashscore работает!\nРазмер данных: {len(r.text)} байт\nПервые 300 символов:\n{r.text[:300]}")
            return r.text
        else:
            send_telegram(f"⚠️ Статус: {r.status_code}")
    except Exception as e:
        send_telegram(f"❌ Ошибка: {e}")
    return None

def run_checks():
    log.info(f"Проверка {datetime.now().strftime('%H:%M')}")
    get_matches()

def main():
    send_telegram("🔍 <b>Тест Flashscore...</b>")
    run_checks()
    schedule.every(CHECK_INTERVAL).minutes.do(run_checks)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
