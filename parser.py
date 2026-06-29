import re

def update_html_seo(weapons_list):
    html_path = "index.html"
    try:
        seo_text = "<h2>Актуальний список мета-зброї Call of Duty Warzone:</h2>\n<ul>\n"
        for wpn in weapons_list:
            name = wpn.get('name', 'Зброя')
            game = wpn.get('game', 'Warzone')
            wpn_class = wpn.get('class', '')
            
            attachments_text = []
            attachments = wpn.get('attachments', [])
            if isinstance(attachments, list):
                for att in attachments:
                    if isinstance(att, dict) and att.get('name'):
                        attachments_text.append(att.get('name'))
                    elif isinstance(att, str) and att.strip():
                        clean_att = att.strip()
                        if clean_att.startswith("-"):
                            clean_att = clean_att[1:].strip()
                        attachments_text.append(clean_att)
            
            modules_str = ", ".join(attachments_text) if attachments_text else "кращі модулі та комплекти"
            seo_text += f"  <li><b>Краща збірка {name} ({game})</b> — клас {wpn_class}. Актуальні мета модулі для комплекту: {modules_str}.</li>\n"
            
        seo_text += "</ul>"

        with open(html_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        pattern = r'(<div id="seo-weapons-index"[^>]*>)(.*?)(</div>)'
        
        if re.search(pattern, html_content, re.DOTALL):
            updated_content = re.sub(pattern, f"\\1\n{seo_text}\n\\3", html_content, flags=re.DOTALL)
            with open(html_path, "w", encoding="utf-8") as file:
                file.write(updated_content)
            print("🚀 [SEO] Текстовий індекс для Googlebot в index.html успішно оновлено!")
        else:
            print("⚠️ [SEO] Попередження: Блок id='seo-weapons-index' не знайдено в index.html. Контент не вшито.")

    except Exception as e:
        print(f"❌ [SEO] Помилка автогенерації тексту для пошукових роботів: {e}")

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
     # СЮДА ВСТАВЛЯЕМ ОДНУ ЭТУ СТРОЧКУ (сразу под закрывающей скобкой переменной):
    update_html_seo(valid_meta)
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
    
    # 🎯 ЗАПУСКАЄМО ПРЕ-РЕНДЕРИНГ ПЕРЕД ВІДПРАВКОЮ ЗВІТУ
    pre_render_html(new_meta['weapons'] if 'new_meta' in locals() and 'weapons' in new_meta else sorted_data if 'sorted_data' in locals() else weapons_list if 'weapons_list' in locals() else [])

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
def update_html_seo(weapons_list):
    html_path = "index.html"
    try:
        # 1. Генерируем чистый текстовый список пушек для Google
        seo_text = "<h2>Актуальний список мета-зброї Warzone:</h2>\n<ul>\n"
        for wpn in weapons_list:
            name = wpn.get('name', '')
            game = wpn.get('game', '')
            wpn_class = wpn.get('class', '')
            seo_text += f"  <li>Мета збірка {name} ({game}) — клас {wpn_class}</li>\n"
        seo_text += "</ul>"

        # 2. Читаем текущий index.html
        with open(html_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        # 3. Находим наш SEO-блок и заменяем его содержимое
        import re
        pattern = r'(<div id="seo-weapons-index"[^>]*>)(.*?)(</div>)'
        
        if re.search(pattern, html_content, re.DOTALL):
            updated_content = re.sub(pattern, f"\\1\n{seo_text}\n\\3", html_content, flags=re.DOTALL)
            
            # 4. Перезаписываем файл
            with open(html_path, "w", encoding="utf-8") as file:
                file.write(updated_content)
            print("📝 SEO-індекс в index.html успішно оновлено!")
        else:
            print("⚠️ SEO-блок id='seo-weapons-index' не знайдено в index.html")

    except Exception as e:
        print(f"❌ Помилка оновлення SEO-тексту: {e}")

# Вызовите эту функцию там, где скрипт успешно скачал `data.weapons`
# update_html_seo(data_weapons)
def pre_render_html(weapons_data):
    """Автоматически генерирует карточки оружия и вшивает их в index.html перед публикацией"""
    try:
        # Сортируем оружие по алфавиту прямо на сервере
        sorted_weapons = sorted(weapons_data, key=lambda x: x.get('name', ''))
        
        cards_html = ""
        for wpn in sorted_weapons:
            attachments_li = ""
            for att in wpn.get('attachments', []):
                cat = f"<span class='att-cat'>{att['category']}:</span> " if att.get('category') else ""
                attachments_li += f"<li class='attachment-item'>{cat}<span class='att-name'>{att['name']}</span></li>"
            
            if not attachments_li:
                attachments_li = "<li class='no-att'>🔧 Збірка уточнюється...</li>"

            # Карточки изначально скрыты (display: none), пока игрок не нажмет категорию
            cards_html += f"""
            <div class="weapon-card" data-class="{wpn.get('class', '')}" data-game="{wpn.get('game', '')}" style="display: none;">
                <div class="rank">#{wpn.get('rank', '')}</div>
                <h2 class="weapon-name">{wpn.get('name', 'Без назви')}</h2>
                <div class="tags">
                    <span class="tag game-tag">{wpn.get('game', 'BO6')}</span>
                    <span class="tag class-tag">{wpn.get('class', 'Зброя')}</span>
                </div>
                <ul class="attachments-list">
                    {attachments_li}
                </ul>
            </div>"""
        
        # Читаем шаблон index.html
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # Заменяем маркер на готовый сгенерированный HTML
        if "<!-- PRE_RENDERED_WEAPONS_PLACEHOLDER -->" in html_content:
            updated_html = html_content.replace("<!-- PRE_RENDERED_WEAPONS_PLACEHOLDER -->", cards_html)
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(updated_html)
            print("🎯 Пре-рендеринг HTML успешно завершен!")
        else:
            print("⚠️ Маркер PRE_RENDERED_WEAPONS_PLACEHOLDER не найден в файле index.html")
    except Exception as e:
        print(f"❌ Ошибка пре-рендеринга: {e}")
def pre_render_html(weapons_data):
    """Автоматически генерирует карточки оружия и вшивает их в index.html перед публикацией"""
    try:
        if not weapons_data:
            print("⚠️ Нет данных о пушках для пре-рендеринга!")
            return
            
        # Сортируем оружие по алфавиту прямо на сервере
        sorted_weapons = sorted(weapons_data, key=lambda x: x.get('name', ''))
        
        cards_html = ""
        for wpn in sorted_weapons:
            attachments_li = ""
            for att in wpn.get('attachments', []):
                cat = f"<span class='att-cat'>{att['category']}:</span> " if att.get('category') else ""
                attachments_li += f"<li class='attachment-item'>{cat}<span class='att-name'>{att['name']}</span></li>"
            
            if not attachments_li:
                attachments_li = "<li class='no-att'>🔧 Збірка уточнюється...</li>"

            # Карточки изначально скрыты (display: none), пока игрок не нажмет категорию
            cards_html += f"""
            <div class="weapon-card" data-class="{wpn.get('class', '')}" data-game="{wpn.get('game', '')}" style="display: none;">
                <div class="rank">#{wpn.get('rank', '')}</div>
                <h2 class="weapon-name">{wpn.get('name', 'Без назви')}</h2>
                <div class="tags">
                    <span class="tag game-tag">{wpn.get('game', 'BO6')}</span>
                    <span class="tag class-tag">{wpn.get('class', 'Зброя')}</span>
                </div>
                <ul class="attachments-list">
                    {attachments_li}
                </ul>
            </div>"""
        
        # Читаем шаблон index.html
        import os
        if not os.path.exists("index.html"):
            print("❌ Файл index.html не найден!")
            return
            
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # Заменяем маркер на готовый сгенерированный HTML
        if "<!-- PRE_RENDERED_WEAPONS_PLACEHOLDER -->" in html_content:
            updated_html = html_content.replace("<!-- PRE_RENDERED_WEAPONS_PLACEHOLDER -->", cards_html)
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(updated_html)
            print("🎯 Пре-рендеринг HTML успешно завершен!")
        else:
            print("⚠️ Маркер PRE_RENDERED_WEAPONS_PLACEHOLDER не найден в файле index.html")
    except Exception as e:
        print(f"❌ Ошибка пре-рендеринга: {e}")
