import requests
import json

def send_news_preview():
    # 🔐 Твої робочі токени та ID чату спільноти
    BOT_TOKEN = "8832958560:AAGSrxEaA4VhsxDumg6YAWMwFr3lnq3P2As"
    CHAT_ID = "-1003771382871"
    TOPIC_ID = 175  # Твоя тема форуму

    # 🎯 ГОЛОВНИЙ ФІКС 1: Вказали пряме посилання на реальний файл картинки
    photo_url = "https://warzone.pp.ua"

    # ✍️ Офіційний кіберспортивний анонс дуелі з HTML-форматуванням
    caption_text = (
        "⚔️ <b>ДУЕЛЬ СЕЗОНУ: AN-94 проти VX Compact!</b>\n\n"
        "🔍 Наш автономний хмарний розбір графіків <b>TTK</b> виявив жорстку приховану імбу! "
        "Укорочена модифікація <i>VX Compact</i> повністю переписує правила гри в ближньому бою.\n\n"
        "📊 <b>Ключові показники дуелі на 02.07.2026:</b>\n"
        "• 💥 <code>VX Compact</code> — <b>580 ms</b> (впритул до 37м) | Дальний: 662 ms\n"
        "• ⚪ <code>AN-94</code> — <b>640 ms</b> (ближній бій) | Дальний: 687 ms\n\n"
        "🚀 Повні інтерактивні графіки віддачі, балістики та швидкості прицілювання (ADS) "
        "вже завантажені та доступні в нашому новинному розділі хабу!"
    )

    # 🎛️ Створюємо велику люксову інлайн-кнопку прямо під фотографією
    reply_markup = {
        "inline_keyboard": [
            [
                {
                    "text": "📰 Читати повний звіт на сайті",
                    "url": "https://warzone.pp.ua/news.html"
                }
            ]
        ]
    }

    # 📡 Формуємо POST-запит до серверів Telegram Bot API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "message_thread_id": TOPIC_ID,  # 🎯 ГОЛОВНИЙ ФІКС 2: Направили пост строго в тему №175
        "photo": photo_url,
        "caption": caption_text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(reply_markup)
    }

    # 🔥 Запуск залпу повідомлення в месенджер
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("🏆 Прев'ю новини успішно доставлено в твою тему Telegram!")
        else:
            print(f"❌ Помилка Telegram API: {response.text}")
    except Exception as e:
        print(f"❌ Збій підключення до мережі: {e}")

if __name__ == "__main__":
    send_news_preview()
