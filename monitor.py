import requests
import time
import logging
from datetime import datetime

TELEGRAM_TOKEN = "7535762489:AAHzzcXt5PxNZ4vpbVuiFb3CYvmErWcD8m4"
CHAT_ID = "5271405408"
CHECK_INTERVAL = 15

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
log = logging.getLogger(__name__)

def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        log.error(f"Ошибка Telegram: {e}")

def get_matches():
    url = "https://www.flashscore.com/feed/football-live"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Fsign": "SW9D1eZo",
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200 or len(resp.content) < 50:
            log.warning("Flashscore вернул пустой ответ")
            return []
        data = resp.json()
        matches = []
        for match in data.get("data", []):
            matches.append({
                "id": match.get("id"),
                "home": match.get("home", {}).get("name", "Unknown"),
                "away": match.get("away", {}).get("name", "Unknown"),
                "odds": match.get("odds", {})
            })
        return matches
    except Exception as e:
        log.error(f"Ошибка Flashscore: {e}")
        return []

def check_anomalies(match):
    signals = []
    odds = match.get("odds", {})
    
    total_5 = odds.get("total_5")
    total_5_5 = odds.get("total_5_5")
    if total_5 and total_5_5 and total_5 > total_5_5:
        signals.append(f"Аномалия тоталов: 5={total_5} > 5.5={total_5_5}")
    
    fonbet = odds.get("fonbet", {}).get("main")
    bet365 = odds.get("1xBet", {}).get("main")
    if fonbet is None and bet365 is not None:
        signals.append("Fonbet не принимает, 1xBet работает")
    
    return signals

def monitor():
    log.info("Мониторинг запущен")
    sent = set()
    
    while True:
        matches = get_matches()
        log.info(f"Найдено матчей: {len(matches)}")
        
        for m in matches:
            signals = check_anomalies(m)
            for sig in signals:
                uid = f"{m['id']}_{sig}"
                if uid in sent:
                    continue
                msg = f"""
⚽ СИГНАЛ
📌 {m['home']} vs {m['away']}
📊 {sig}
🕐 {datetime.now().strftime('%H:%M')}
"""
                send_telegram(msg.strip())
                sent.add(uid)
        
        time.sleep(CHECK_INTERVAL * 60)

if __name__ == "__main__":
    monitor()
