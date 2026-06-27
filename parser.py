import json
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

URL = "https://wzranked.com/games/call-of-duty-warzone/meta/builds"

def clean_text_block(text):
    """Очищает и разбивает сырой текст страницы на массив значимых строк."""
    # Разбиваем по строкам, убираем пробелы по краям
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Ищем, где начинается список оружия (обычно со знака # 1 или цифры 1)
    start_index = 0
    for i, line in enumerate(lines):
        if line == "# 1" or line == "1":
            start_index = i
            break
            
    # Возвращаем только ту часть текста, где идет список оружия
    return lines[start_index:]

def parse_weapons(lines):
    """Разбирает очищенные строки текста в структурированный JSON."""
    weapons = []
    current_weapon = None
    
    iterator = iter(lines)
    for line in iterator:
        # Проверяем, начинается ли блок с номера оружия (например, "# 1" или просто "1")
        if re.match(r"^#?\s*\d+$", line):
            # Если уже собиралось предыдущее оружие, сохраняем его
            if current_weapon and current_weapon["attachments"]:
                weapons.append(current_weapon)
                
            rank = line.replace("#", "").strip()
            
            try:
                name = next(iterator)      # Следующая строка — название (напр., Carbon 57)
                game = next(iterator)      # Затем — игра (напр., BO7)
                w_class = next(iterator)   # Затем — класс (напр., SMG)
                
                # Пропускаем возможный дубль названия, если он есть в разметке
                possible_duplicate = next(iterator)
                if possible_duplicate != name:
                    # Если это не дубль, а уже модуль, вернем итератор на шаг назад
                    # Но в структуре wzranked после класса обычно идет повтор имени, поэтому просто считываем модули
                    pass

                current_weapon = {
                    "rank": int(rank),
                    "name": name,
                    "game": game,
                    "class": w_class,
                    "attachments": []
                }
            except StopIteration:
                break
                
        # Если строка начинается с дефиса (или это просто модуль), добавляем в текущее оружие
        elif current_weapon and (line.startswith("-") or len(line) > 3):
            clean_attachment = line.lstrip("- ").strip()
            # Проверяем, чтобы случайно не добавить имя следующего оружия как модуль
            if "BO7" not in line and "BO6" not in line and "MW3" not in line:
                current_weapon["attachments"].append(clean_attachment)
                
    # Не забываем добавить последнее обработанное оружие
    if current_weapon and current_weapon["attachments"]:
        weapons.append(current_weapon)
        
    return weapons

def main():
    print("🚀 WZ_Only_UA: Запуск фонового браузера...")
    
    with sync_playwright() as p:
        # Запускаем браузер в режиме headless=True (скрытый)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"📦 Открываем страницу: {URL}")
        # Ждем пока загрузится сеть, чтобы отработали все скрипты сайта
        page.goto(URL, wait_until="networkidle")
        
        # Получаем полный HTML страницы
        html = page.content()
        browser.close()
        
    print("🔍 Анализ полученных данных...")
    soup = BeautifulSoup(html, "html.parser")
    
    # Берем весь текст со страницы, так как структура сайта имеет четкий текстовый порядок
    raw_text = soup.get_text(separator="\n")
    
    # Очищаем текст и оставляем только блок с пушками
    cleaned_lines = clean_text_block(raw_text)
    
    # Парсим строки в список словарей
    result_meta = parse_weapons(cleaned_lines)
    
    # Сохраняем результат в локальный JSON-файл
    output_file = "wz_meta_ua.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result_meta, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Готово! Спарсено пушек: {len(result_meta)}. Данные сохранены в файл: {output_file}")

if __name__ == "__main__":
    main()
