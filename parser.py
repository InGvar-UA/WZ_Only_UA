import json
import re
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

URL = "https://wzranked.com/games/call-of-duty-warzone/meta/builds"

def clean_text_block(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    start_index = 0
    for i, line in enumerate(lines):
        if line == "# 1" or line == "1":
            start_index = i
            break
    return lines[start_index:]

def parse_weapons(lines):
    weapons = []
    current_weapon = None
    iterator = iter(lines)
    
    known_categories = [
        "Muzzle", "Barrel", "Laser", "Optic", "Stock", "Rear Grip", 
        "Magazine", "Ammo", "Underbarrel", "Comb", "Guard", 
        "Fire Mods", "Conversion Kit", "Perk", "Bolt", "Rail"
    ]
    
    for line in iterator:
        if re.match(r"^#?\s*\d+$", line):
            if current_weapon and current_weapon["attachments"]:
                weapons.append(current_weapon)
                
            rank = line.replace("#", "").strip()
            try:
                name = next(iterator)
                game = next(iterator)
                w_class = next(iterator)
                
                current_weapon = {
                    "rank": int(rank),
                    "name": name,
                    "game": game,
                    "class": w_class,
                    "attachments": []
                }
            except StopIteration:
                break
        elif current_weapon and len(line) > 1:
            if line in [current_weapon["name"], current_weapon["game"], current_weapon["class"], "BO7", "BO6", "MW3"]:
                continue
            
            clean_line = line.lstrip("- ").strip()
            
            matched_cat = None
            for cat in known_categories:
                if clean_line.startswith(cat):
                    matched_cat = cat
                    break
            
            if matched_cat:
                att_name = clean_line[len(matched_cat):].strip()
                current_weapon["attachments"].append({
                    "category": matched_cat,
                    "name": att_name
                })
            else:
                category = ""
                lower_line = clean_line.lower()
                
                if any(k in lower_line for k in ['brake', 'suppressor', 'compensator', 'silencer', 'choke']): category = "Muzzle"
                elif 'barrel' in lower_line: category = "Barrel"
                elif 'laser' in lower_line: category = "Laser"
                elif any(k in lower_line for k in ['optic', 'sight', 'scope']): category = "Optic"
                elif 'stock' in lower_line: category = "Stock"
                elif 'grip' in lower_line: category = "Rear Grip"
                elif any(k in lower_line for k in ['mag', 'drum', 'round']): category = "Magazine"
                elif any(k in lower_line for k in ['handstop', 'foregrip']): category = "Underbarrel"
                
                if category:
                    current_weapon["attachments"].append({
                        "category": category,
                        "name": clean_line
                    })
                else:
                    current_weapon["attachments"].append({
                        "category": "🔧",
                        "name": clean_line
                    })
                
    if current_weapon and current_weapon["attachments"]:
        weapons.append(current_weapon)
    return weapons

    if current_weapon and current_weapon["attachments"]:
        weapons.append(current_weapon)
    return weapons

def main():
    print("🚀 WZ_Only_UA: Сбор чистых данных с фиксацией времени...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")
        html = page.content()
        browser.close()
        
    soup = BeautifulSoup(html, "html.parser")
    raw_text = soup.get_text(separator="\n")
    cleaned_lines = clean_text_block(raw_text)
    result_meta = parse_weapons(cleaned_lines)
    
    valid_meta = [w for w in result_meta if len(w["attachments"]) > 0]
    
        # 🕒 Расчет времени: берем UTC-время (сервера GitHub) и переводим на Киев (+3 часа)
    from datetime import datetime, timedelta
    kyiv_time = datetime.utcnow() + timedelta(hours=3)
    last_update_string = kyiv_time.strftime("%d.%m.%Y %H:%M")

    # Формируем новую структуру JSON: сохраняем и дату, и массив пушек
    final_json_data = {
        "last_updated": last_update_string,
        "weapons": valid_meta
    }
    
    # =====================================================================
    # 🤖 СИСТЕМА РОЗУМНИХ ТЕЛЕГРАМ-СПОВІЩЕНЬ ПРО АУДИТ МЕТИ
    # =====================================================================
    import os
    
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    file_path = "wz_meta_ua.json"
    
    # 1. Завантажуємо старі дані з файлу для порівняння
    old_weapons_list = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                old_json = json.load(f)
                # Якщо у старому файлі вже була структура зі словником, беремо масив
                old_weapons_list = old_json.get("weapons", []) if isinstance(old_json, dict) else old_json
        except Exception:
            old_weapons_list = []

    # Перетворюємо старі пушки на словник для швидкого порівняння модулів за ім'ям
    old_weapons_map = {w['name']: w for w in old_weapons_list}
    changed_weapons = []

    # 2. Скануємо нові пушки та шукаємо, що саме змінилося
    for new_w in valid_meta:
        w_name = new_w['name']
        if w_name in old_weapons_map:
            old_w = old_weapons_map[w_name]
            # Порівнюємо список модулів (attachments) символ у символ
            if json.dumps(new_w.get('attachments')) != json.dumps(old_w.get('attachments')):
                changed_weapons.append(w_name)
        else:
            # З'явилася абсолютно нова гармата в базі
            changed_weapons.append(f"🆕 {w_name}")

    # 3. Формуємо красивий текст повідомлення залежно від результату
    if not changed_weapons:
        # ЛОГІКА 1: Змін у балансі зброї немає
        tg_message = (
            "🤖 <b>Щоденний аудит Мети Warzone</b>\n\n"
            "🔍 Хмарний парсер успішно завершив перевірку серверів CoD.\n"
            "🛑 <b>Змін у балансі зброї немає.</b>\n\n"
            "✅ У додатку та на сайті відображаються 100% актуальні та перевірені збірки!\n\n"
            "🌐 <b>Відкрити сайт:</b> warzone.pp.ua\n"
            "🚀 <b>Запустити Mini App:</b> t.me/warzone_only_ua_bot/meta"
        )
        print("📝 Змін у балансі немає. Буде надіслано звіт про актуальність.")
    else:
        # ЛОГІКА 2: Мета змінилася!
        weapons_list = ", ".join(changed_weapons)
        tg_message = (
            "🔥 <b>Увага! Мета Warzone змінилася!</b>\n\n"
            "⚠️ Розробники оновили актуальні сетапи для наступної зброї:\n"
            f"👉 <b>{weapons_list}</b>\n\n"
            "⚡ Робот уже переписав базу даних. Усі свіжі модулі та топові класи вже доступні на наших платформах!\n\n"
            "🌐 <b>Дивитись нові збірки:</b> warzone.pp.ua\n"
            "🚀 <b>Відкрити в Telegram:</b> t.me/warzone_only_ua_bot/meta"
        )
        print(f"📝 Мета змінилася для: {weapons_list}. Готую штормове попередження!")

    # 4. Фізично зберігаємо оновлений JSON-файл у проект
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(final_json_data, f, indent=4, ensure_ascii=False)
    print(f"✅ Успішно збережено! Зображено пушек: {len(valid_meta)}. Час: {last_update_string}")

    # 5. Надсилаємо сформований звіт у твій Телеграм-канал
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "message_thread_id": 175, # 🎯 ОБОВ'ЯЗКОВО ПОСТАВИЛИ КОМУ В КІНЦІ РЯДКА!
            "text": tg_message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        try:
            requests.post(url, json=payload, timeout=10)
            print("📢 Звіт успішно відправлено в Телеграм-канал!")
        except Exception as e:
            print(f"❌ Помилка надсилання в ТГ: {e}")
    else:
        print("⚠️ Telegram сетинги не знайдені в GitHub Secrets. Звіт у месенджер пропущено.")

if __name__ == "__main__":
    main()
