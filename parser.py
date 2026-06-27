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
            if "BO7" not in line and "BO6" not in line and "MW3" not in line:
                current_weapon["attachments"].append(line)
                
    if current_weapon and current_weapon["attachments"]:
        weapons.append(current_weapon)
    return weapons

def main():
    print("🚀 WZ_Only_UA: Запуск фонового браузера...")
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
