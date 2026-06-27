import json
import re
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
    
    # Список известных категорий для сверки
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
            # Убираем технический мусор сайта
            if line in [current_weapon["name"], current_weapon["game"], current_weapon["class"], "BO7", "BO6", "MW3"]:
                continue
            
            clean_line = line.lstrip("- ").strip()
            
            # Проверяем, начинается ли строка с известной категории
            matched_cat = None
            for cat in known_categories:
                if clean_line.startswith(cat):
                    matched_cat = cat
                    break
            
            if matched_cat:
                # Отрезаем категорию, оставляем только название модуля
                att_name = clean_line[len(matched_cat):].strip()
                current_weapon["attachments"].append({
                    "category": matched_cat,
                    "name": att_name
                })
            else:
                # Если категория пропущена в тексте (как у Muzzle), пытаемся угадать её по ключевым словам
                category = ""
                lower_line = clean_line.toLowerCase() if hasattr(clean_line, 'toLowerCase') else clean_line.lower()
                
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
                    # Если совсем не распознали категорию, сохраняем как общий модуль
                    current_weapon["attachments"].append({
                        "category": "🔧",
                        "name": clean_line
                    })
                
    if current_weapon and current_weapon["attachments"]:
        weapons.append(current_weapon)
    return weapons

def main():
    print("🚀 WZ_Only_UA: Запуск проверенного текстового парсера...")
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
    
    with open("wz_meta_ua.json", "w", encoding="utf-8") as f:
        json.dump(result_meta, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Готово! Собрано пушек: {len(result_meta)}.")

if __name__ == "__main__":
    main()
