import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Timezone
TIMEZONE = "Europe/Simferopol"

# Ключи намазов
PRAYER_KEYS = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]

# Названия намазов - разные стили
PRAYER_NAMES_STYLES = {
    "standard": {
        "fajr": "🌙 Фаджр",
        "sunrise": "🌅 Восход",
        "dhuhr": "☀️ Зухр",
        "asr": "🌤 Аср",
        "maghrib": "🌇 Магриб",
        "isha": "🌃 Иша"
    },
    "crimean_cyrillic": {
        "fajr": "🌙 Имсак",
        "sunrise": "🌅 Кунеш",
        "dhuhr": "☀️ Уйле",
        "asr": "🌤 Экинди",
        "maghrib": "🌇 Акъшам",
        "isha": "🌃 Ятсы"
    },
    "crimean_latin": {
        "fajr": "🌙 İmsak",
        "sunrise": "🌅 Küneş",
        "dhuhr": "☀️ Üyle",
        "asr": "🌤 Ekindi",
        "maghrib": "🌇 Aqşam",
        "isha": "🌃 Yatsı"
    }
}

# Стандартные названия (для обратной совместимости)
PRAYER_NAMES = PRAYER_NAMES_STYLES["standard"]

# Названия месяцев хиджри
HIJRI_MONTHS = {
    "cyrillic": [
        "", "Мухаррем", "Сефер", "Ребиу'ль-эвель", "Ребиу'ль-ахыр",
        "Джумазие'ль-эвель", "Джумазие'ль-ахыр", "Реджеб", "Шабан",
        "Рамазан", "Шевваль", "Зилькаде", "Зильхидждже"
    ],
    "latin": [
        "", "Muharrem", "Sefer", "Rebiu'l-evel", "Rebiu'l-ahır",
        "Cumaziye'l-evel", "Cumaziye'l-ahır", "Receb", "Şaban",
        "Ramazan", "Şevval", "Zilkade", "Zilhicce"
    ]
}

# Праздники и особые дни 2026 года
# Формат: (месяц, день): {"name": название, "type": тип, "night": является ли священной ночью}
HOLIDAYS = {
    2026: {
        (1, 16): {"name": "Мирадж геджеси", "type": "night", "night": True},
        (2, 3): {"name": "Бераат геджеси", "type": "night", "night": True},
        (2, 19): {"name": "Рамазан айынынъ башланувы", "type": "start", "night": False},
        (3, 17): {"name": "Къадир геджеси", "type": "night", "night": True},
        (1, 19): {"name": "Ораза байрамынынъ арефеси", "type": "eve", "night": False},
        (3, 20): {"name": "Ораза байрамы", "type": "holiday", "night": False},
        (3, 21): {"name": "Ораза байрамы", "type": "holiday", "night": False},
        (3, 22): {"name": "Ораза байрамы", "type": "holiday", "night": False},
        (5, 26): {"name": "Арефе куню", "type": "eve", "night": False},
        (5, 27): {"name": "Къурбан байрамы", "type": "holiday", "night": False},
        (5, 28): {"name": "Къурбан байрамы", "type": "holiday", "night": False},
        (5, 29): {"name": "Къурбан байрамы", "type": "holiday", "night": False},
        (5, 30): {"name": "Къурбан байрамы", "type": "holiday", "night": False},
        (6, 16): {"name": "Хиджрий йыл башы (1448 с.)", "type": "new_year", "night": False},
        (6, 25): {"name": "Ашуре куню", "type": "special", "night": False},
        (8, 25): {"name": "Мевлид геджеси", "type": "night", "night": True},
        (12, 10): {"name": "Учь айларнынъ башланувы", "type": "start", "night": False},
        (12, 11): {"name": "Регъаиб геджеси", "type": "night", "night": True},
    }
}

# Рамазан периоды (для обратного отсчёта)
RAMADAN_PERIODS = {
    2026: {
        "start": date(2026, 2, 19),
        "end": date(2026, 3, 20),  # первый день Ораза байрамы
    }
}

# Путь к CSV файлу
CSV_PATH = "data/prayer_times.csv"

# База данных
DATABASE_PATH = "data/prayer_bot.db"