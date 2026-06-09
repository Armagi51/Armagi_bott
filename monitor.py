import requests
import time
import json
import os
import logging
from datetime import datetime, timedelta

# ========== НАСТРОЙКИ (ТОЛЬКО ЭТО МЕНЯЕШЬ) ==========
ODDS_API_KEY = "2a78dddf67196c207eb922fc1f8fef7b"   # <- вставь свой ключ из Odds API
TELEGRAM_TOKEN = "7535762489:AAHzzcXt5PxNZ4vpbVuiFb3CYvmErWcD8m4"
CHAT_ID = "5271405408"
CHECK_INTERVAL_HOURS = 1.5  # каждые 1.5 часа
# ====================================================

HISTORY_FILE = "history.json"  # файл для хранения истории кефов
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
        log.error(f"Telegram ошибка: {e}")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def clean_old_data(history):
    cutoff = datetime.now() - timedelta(hours=72)
    new_history = {}
    for match_id, entries in history.items():
        new_entries = [e for e in entries if datetime.fromisoformat(e["timestamp"]) > cutoff]
        if new_entries:
            new_history[match_id] = new_entries
    return new_history

def get_current_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h&oddsFormat=decimal"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            log.error(f"Odds API ошибка {resp.status_code}: {resp.text[:200]}")
            return []
        data = resp.json()
        matches = []
        for match in data:
            bookmakers = match.get("bookmakers", [])
            best_odds = {}
            for bm in bookmakers:
                if bm["key"] in ["bet365", "pinnacle", "williamhill", "unibet"]:
                    for market in bm.get("markets", []):
                        if market["key"] == "h2h":
                            outcomes = market.get("outcomes", [])
                            if len(outcomes) >= 3:
                                best_odds[bm["key"]] = {
                                    "home": outcomes[0]["price"],
                                    "draw": outcomes[1]["price"],
                                    "away": outcomes[2]["price"]
                                }
                            break
            if best_odds:
                matches.append({
                    "id": match["id"],
                    "home": match["home_team"],
                    "away": match["away_team"],
                    "commence_time": match["commence_time"],
                    "odds": best_odds,
                    "timestamp": datetime.now().isoformat()
                })
        return matches
    except Exception as e:
        log.error(f"Ошибка получения данных: {e}")
        return []

def detect_drops(match_id, current_odds_dict, history):
    signals = []
    if match_id not in history:
        return signals, history
    
    last_entry = history[match_id][-1] if history[match_id] else None
    if not last_entry:
        return signals, history
    
    for bm, odds in current_odds_dict.items():
        if bm not in last_entry["odds"]:
            continue
        prev_home = last_entry["odds"][bm].get("home")
        curr_home = odds.get("home")
        if prev_home and curr_home and curr_home < prev_home:
            drop_pct = round((prev_home - curr_home) / prev_home * 100, 1)
            if drop_pct >= 8:  # падение на 8% и больше
                signals.append(f"📉 {bm} home: {prev_home} → {curr_home} (-{drop_pct}%)")
        
        prev_away = last_entry["odds"][bm].get("away")
        curr_away = odds.get("away")
        if prev_away and curr_away and curr_away < prev_away:
            drop_pct = round((prev_away - curr_away) / prev_away * 100, 1)
            if drop_pct >= 8:
                signals.append(f"📉 {bm} away: {prev_away} → {curr_away} (-{drop_pct}%)")
    
    return signals, history

def update_history(match_id, match_data, history):
    if match_id not in history:
        history[match_id] = []
    history[match_id].append({
        "timestamp": match_data["timestamp"],
        "odds": match_data["odds"]
    })
    return history

def monitor():
    log.info("🚀 Мониторинг запущен (Odds API)")
    history = load_history()
    
    while True:
        log.info("🔄 Запрос текущих коэффициентов...")
        matches = get_current_odds()
        log.info(f"✅ Получено матчей: {len(matches)}")
        
        for match in matches:
            match_id = match["id"]
            match_name = f"{match['home']} vs {match['away']}"
            
            # Проверяем падения
            signals, history = detect_drops(match_id, match["odds"], history)
            
            # Обновляем историю
            history = update_history(match_id, match, history)
            
            # Отправляем сигналы
            for sig in signals:
                msg = f"""
⚽ СИГНАЛ ПАДЕНИЯ
📌 {match_name}
📊 {sig}
🕐 {datetime.now().strftime('%H:%M')}
"""
                send_telegram(msg.strip())
                log.info(f"Сигнал отправлен: {match_name} - {sig}")
        
        # Чистим старые данные (раз в 10 циклов, чтобы не нагружать)
        if int(time.time()) % (10 * int(CHECK_INTERVAL_HOURS * 3600)) < CHECK_INTERVAL_HOURS * 3600:
            old_size = len(history)
            history = clean_old_data(history)
            log.info(f"🧹 Очистка истории: было {old_size} матчей, стало {len(history)}")
        
        save_history(history)
        log.info(f"💾 История сохранена. Всего матчей в истории: {len(history)}")
        log.info(f"😴 Следующий запрос через {CHECK_INTERVAL_HOURS} часа(-ов)")
        time.sleep(CHECK_INTERVAL_HOURS * 3600)

if __name__ == "__main__":
    monitor()
