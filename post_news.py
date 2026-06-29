import requests

# Токен твоего бота из @BotFather
BOT_TOKEN = "8832958560:AAGSrxEaA4VhsxDumg6YAWMwFr3lnq3P2As"

# Данные группы и ветки (топика)
CHAT_ID = "-1003771382871"
TOPIC_ID = 175

# Повідомлення про чтото
text = """🚀 <b>Наш бот автоматически !</b>

Друзі, технічні роботи та приєднання власного домену успішно закінчено! Наш сервіс Call of Duty: Warzone повністю перейшов на нову, преміальну та незалежну адресу: 

🌐 <b><a href="https://www.warzone.pp.ua">www.warzone.pp.ua</a></b>

<b>Що це означає для вас:</b>
• 📱 <b>Telegram Mini App</b> тепер відкривається миттєво та адаптований під абсолютно будь-який екран смартфона.
• ⚡ Наша інтерактивна база знань стала ще швидшою, отримала розумний живий пошук та зручні категорії зброї.
• 🤖 Система повністю автономна — хмарні сервери оновлюватимуть мета-збірки щоночі, щоб ви завжди мали свіжі сетапи.

Додаток уже працює у звичайному стабільному режимі як за прямим посиланням у браузері, так і прямо всередині Telegram через кнопку меню!

Запускайте Mini App, оцінюйте новий дизайн та перемагайте на полі бою! Дякуємо, що ви з нами! 🇺🇦🔥"""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Инлайн-кнопка с новым адресом домена
reply_markup = {
    "inline_keyboard": [
        [
            {
                "text": "🚀 Відкрити Warzone Only UA",
                "url": "https://www.warzone.pp.ua"
            }
        ]
    ]
}

payload = {
    "chat_id": CHAT_ID,
    "message_thread_id": TOPIC_ID,
    "text": text,
    "parse_mode": "HTML",
    "reply_markup": reply_markup
}

print("Отправка релизной новости о запуске домена (HTML режим)...")
response = requests.post(url, json=payload)

if response.status_code == 200:
    print("✅ Финальная новость о релизе успешно опубликована в Telegram!")
else:
    print(f"❌ Ошибка отправки: {response.text}")
