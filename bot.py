import asyncio
import json
from datetime import datetime
from aiogram import Bot, Dispatcher
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

API_TOKEN = '7535762489:AAHzzcXt5PxNZ4vpbVuiFb3CYvmErWcD8m4'
USER_ID = 5271405408

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

URL = "https://nb-bet.com/"

async def fetch_odds():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(URL)

    await asyncio.sleep(5)  # Подождем загрузку страницы

    matches = driver.find_elements("xpath", '//div[contains(@class, "coeff-line")]')

    odds_data = {}

    for match in matches:
        try:
            teams = match.find_element("xpath", './/div[contains(@class, "team-name")]').text
            odds = match.find_element("xpath", './/div[contains(@class, "coeff")]').text
            odds_data[teams] = odds
        except Exception:
            continue

    driver.quit()

    return odds_data

async def check_odds():
    try:
        with open('odds_data.json', 'r', encoding='utf-8') as f:
            previous_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        previous_data = {}

    current_data = await fetch_odds()

    fallen = []

    for teams, current_odds in current_data.items():
        prev_odds = previous_data.get(teams)
        if prev_odds and current_odds != prev_odds:
            fallen.append((teams, prev_odds, current_odds))

    if fallen:
        text = f"Изменения коэффициентов ({datetime.now().strftime('%H:%M:%S')}):\n\n"
        for item in fallen:
            text += f"{item[0]}: {item[1]} ➔ {item[2]}\n"
        await bot.send_message(chat_id=USER_ID, text=text)

    with open('odds_data.json', 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=4)

async def main():
    while True:
        await check_odds()
        await asyncio.sleep(600)  # Каждые 10 минут

if __name__ == "__main__":
    asyncio.run(main())