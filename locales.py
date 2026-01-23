TEXTS = {
    "ru": {
        "main_menu_title": "🕌 <b>Главное меню</b>\n\nВыберите действие:",
        "btn_schedule": "📅 Расписание",
        "btn_tomorrow": "📅 Завтра",
        "btn_today": "📅 Сегодня",
        "btn_next": "⏰ Следующий намаз",
        "btn_settings": "⚙️ Настройки",
        "btn_language": "🌐 Язык / Til",
        "btn_back": "◀️ Назад",
        "settings_title": "⚙️ <b>Настройки</b>",
        "language_select": "🌐 <b>Выберите язык / Tilni saylañız:</b>",
        "lang_ru": "🇷🇺 Русский",
        "lang_crh_cyr": "🇺🇦 Къырымтатар (Кирилл)",
        "lang_crh_lat": "🇺🇦 Qırımtatar (Latin)",
        "changed_lang": "✅ Язык изменен на Русский",
        # Добавьте остальные фразы сюда...
    },
    "crh_cyr": {
        "main_menu_title": "🕌 <b>Баш меню</b>\n\nАрекетни сайланъыз:",
        "btn_schedule": "📅 Джедвель",
        "btn_tomorrow": "📅 Ярын",
        "btn_today": "📅 Бугунь",
        "btn_next": "⏰ Невбеттеки намаз",
        "btn_settings": "⚙️ Айярлар",
        "btn_language": "🌐 Тиль / Язык",
        "btn_back": "◀️ Кери",
        "settings_title": "⚙️ <b>Айярлар</b>",
        "language_select": "🌐 <b>Тильни сайланъыз / Выберите язык:</b>",
        "lang_ru": "🇷🇺 Русский",
        "lang_crh_cyr": "🇺🇦 Къырымтатар (Кирилл)",
        "lang_crh_lat": "🇺🇦 Qırımtatar (Latin)",
        "changed_lang": "✅ Тиль Къырымтатарджагъа (Кирилл) денъиштирилди",
    },
    "crh_lat": {
        "main_menu_title": "🕌 <b>Baş menü</b>\n\nAreketni saylañız:",
        "btn_schedule": "📅 Cedvel",
        "btn_tomorrow": "📅 Yarın",
        "btn_today": "📅 Bugün",
        "btn_next": "⏰ Nevbetteki namaz",
        "btn_settings": "⚙️ Ayarlar",
        "btn_language": "🌐 Til / Язык",
        "btn_back": "◀️ Keri",
        "settings_title": "⚙️ <b>Ayarlar</b>",
        "language_select": "🌐 <b>Tilni saylañız / Выберите язык:</b>",
        "lang_ru": "🇷🇺 Русский",
        "lang_crh_cyr": "🇺🇦 Qırımtatar (Kirill)",
        "lang_crh_lat": "🇺🇦 Qırımtatar (Latin)",
        "changed_lang": "✅ Til Qırımtatarcağa (Latin) deñiştirildi",
    }
}

def get_text(lang: str, key: str) -> str:
    """Получить текст по ключу и языку"""
    return TEXTS.get(lang, TEXTS["ru"]).get(key, key)