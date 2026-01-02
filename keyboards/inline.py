from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import PRAYER_NAMES_STYLES, PRAYER_KEYS


def get_prayer_names(style: str = "standard"):
    return PRAYER_NAMES_STYLES.get(style, PRAYER_NAMES_STYLES["standard"])


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📅 Расписание", callback_data="schedule"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    )
    builder.row(
        InlineKeyboardButton(text="🔔 Напоминания", callback_data="reminders"),
        InlineKeyboardButton(text="📍 Локация", callback_data="location")
    )
    builder.row(
        InlineKeyboardButton(text="🎉 Праздники", callback_data="holidays"),
        InlineKeyboardButton(text="❓ Помощь", callback_data="help")
    )
    
    return builder.as_markup()


def schedule_keyboard() -> InlineKeyboardMarkup:
    """Меню расписания"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📅 Сегодня", callback_data="schedule_today"),
        InlineKeyboardButton(text="📅 Завтра", callback_data="schedule_tomorrow")
    )
    builder.row(
        InlineKeyboardButton(text="⏰ Следующий намаз", callback_data="next_prayer")
    )
    builder.row(
        InlineKeyboardButton(text="📆 Выбрать дату", callback_data="schedule_custom_date")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()


def date_navigation_keyboard(current_date: str) -> InlineKeyboardMarkup:
    """Навигация по датам"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="◀️ -7 дн", callback_data=f"date_nav_{current_date}_-7"),
        InlineKeyboardButton(text="◀️ -1", callback_data=f"date_nav_{current_date}_-1"),
        InlineKeyboardButton(text="+1 ▶️", callback_data=f"date_nav_{current_date}_+1"),
        InlineKeyboardButton(text="+7 дн ▶️", callback_data=f"date_nav_{current_date}_+7"),
    )
    builder.row(
        InlineKeyboardButton(text="📅 Сегодня", callback_data="schedule_today"),
        InlineKeyboardButton(text="✏️ Ввести дату", callback_data="schedule_enter_date")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="schedule")
    )
    
    return builder.as_markup()


def settings_keyboard() -> InlineKeyboardMarkup:
    """Меню настроек"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="⏰ Авто-расписание", callback_data="settings_auto")
    )
    builder.row(
        InlineKeyboardButton(text="⏱ Смещение времени", callback_data="settings_offset")
    )
    builder.row(
        InlineKeyboardButton(text="📆 День расписания", callback_data="settings_day")
    )
    builder.row(
        InlineKeyboardButton(text="🔤 Названия намазов", callback_data="settings_prayer_names")
    )
    builder.row(
        InlineKeyboardButton(text="📅 Настройки хиджри", callback_data="settings_hijri")
    )
    builder.row(
        InlineKeyboardButton(text="📍 Настройки локации", callback_data="settings_location")
    )
    builder.row(
        InlineKeyboardButton(text="🎉 Праздники", callback_data="settings_holidays")
    )
    builder.row(
        InlineKeyboardButton(text="🔔 Напоминания", callback_data="reminders")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()


def prayer_names_style_keyboard(current: str = "standard") -> InlineKeyboardMarkup:
    """Выбор стиля названий намазов"""
    builder = InlineKeyboardBuilder()
    
    styles = [
        ("standard", "Стандартные (Фаджр, Зухр...)"),
        ("crimean_cyrillic", "Кириллица (Имсак, Уйле...)"),
        ("crimean_latin", "Латиница (İmsak, Üyle...)")
    ]
    
    for style_key, style_name in styles:
        prefix = "✅ " if current == style_key else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{prefix}{style_name}",
                callback_data=f"set_prayer_style_{style_key}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings")
    )
    
    return builder.as_markup()


def hijri_settings_keyboard(show_hijri: bool = True, style: str = "cyrillic") -> InlineKeyboardMarkup:
    """Настройки хиджри"""
    builder = InlineKeyboardBuilder()
    
    # Показывать/скрывать
    show_text = "✅ Показывать хиджри" if show_hijri else "⬜ Показывать хиджри"
    builder.row(
        InlineKeyboardButton(text=show_text, callback_data="toggle_hijri")
    )
    
    # Стиль месяцев
    builder.row(
        InlineKeyboardButton(
            text=f"{'✅' if style == 'cyrillic' else '⬜'} Кириллица",
            callback_data="set_hijri_style_cyrillic"
        ),
        InlineKeyboardButton(
            text=f"{'✅' if style == 'latin' else '⬜'} Латиница",
            callback_data="set_hijri_style_latin"
        )
    )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings")
    )
    
    return builder.as_markup()


def location_settings_keyboard(show_location: bool = True) -> InlineKeyboardMarkup:
    """Настройки локации"""
    builder = InlineKeyboardBuilder()
    
    # Показывать/скрывать
    show_text = "✅ Показывать в расписании" if show_location else "⬜ Показывать в расписании"
    builder.row(
        InlineKeyboardButton(text=show_text, callback_data="toggle_location_display")
    )
    
    builder.row(
        InlineKeyboardButton(text="📝 Изменить название", callback_data="edit_location_name")
    )
    
    builder.row(
        InlineKeyboardButton(text="🏙 Выбрать город", callback_data="location")
    )
    
    builder.row(
        InlineKeyboardButton(text="⏱ Ручной ввод смещения", callback_data="manual_offset")
    )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings")
    )
    
    return builder.as_markup()


def holidays_settings_keyboard(show_holidays: bool = True) -> InlineKeyboardMarkup:
    """Настройки праздников"""
    builder = InlineKeyboardBuilder()
    
    show_text = "✅ Показывать праздники" if show_holidays else "⬜ Показывать праздники"
    builder.row(
        InlineKeyboardButton(text=show_text, callback_data="toggle_holidays")
    )
    
    builder.row(
        InlineKeyboardButton(text="📋 Список праздников", callback_data="holidays_list")
    )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings")
    )
    
    return builder.as_markup()


def auto_schedule_keyboard(current_time: str = None) -> InlineKeyboardMarkup:
    """Настройка авто-расписания"""
    builder = InlineKeyboardBuilder()
    
    times = ["06:00", "07:00", "08:00", "09:00", "20:00", "21:00"]
    
    for i in range(0, len(times), 3):
        row_times = times[i:i+3]
        builder.row(*[
            InlineKeyboardButton(
                text=f"{'✅ ' if t == current_time else ''}{t}",
                callback_data=f"set_auto_time_{t}"
            )
            for t in row_times
        ])
    
    builder.row(
        InlineKeyboardButton(text="✏️ Своё время", callback_data="set_auto_time_custom")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отключить", callback_data="set_auto_time_off")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings")
    )
    
    return builder.as_markup()


def offset_keyboard(current_offset: int = 0) -> InlineKeyboardMarkup:
    """Настройка смещения времени"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="-30", callback_data="offset_-30"),
        InlineKeyboardButton(text="-15", callback_data="offset_-15"),
        InlineKeyboardButton(text="-5", callback_data="offset_-5"),
    )
    builder.row(
        InlineKeyboardButton(text="+5", callback_data="offset_+5"),
        InlineKeyboardButton(text="+15", callback_data="offset_+15"),
        InlineKeyboardButton(text="+30", callback_data="offset_+30"),
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="manual_offset")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Сбросить (0)", callback_data="offset_reset")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ По намазам", callback_data="offset_per_prayer")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings")
    )
    
    return builder.as_markup()


def prayer_offset_keyboard(prayer_names_style: str = "standard") -> InlineKeyboardMarkup:
    """Выбор намаза для индивидуального смещения"""
    builder = InlineKeyboardBuilder()
    prayer_names = get_prayer_names(prayer_names_style)
    
    for prayer_key in PRAYER_KEYS:
        builder.row(
            InlineKeyboardButton(
                text=prayer_names[prayer_key],
                callback_data=f"prayer_offset_{prayer_key}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings_offset")
    )
    
    return builder.as_markup()


def prayer_offset_value_keyboard(prayer_key: str, current_offset: int = 0) -> InlineKeyboardMarkup:
    """Установка смещения для конкретного намаза"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="-15", callback_data=f"set_prayer_offset_{prayer_key}_-15"),
        InlineKeyboardButton(text="-5", callback_data=f"set_prayer_offset_{prayer_key}_-5"),
        InlineKeyboardButton(text="-1", callback_data=f"set_prayer_offset_{prayer_key}_-1"),
    )
    builder.row(
        InlineKeyboardButton(text="+1", callback_data=f"set_prayer_offset_{prayer_key}_+1"),
        InlineKeyboardButton(text="+5", callback_data=f"set_prayer_offset_{prayer_key}_+5"),
        InlineKeyboardButton(text="+15", callback_data=f"set_prayer_offset_{prayer_key}_+15"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Сбросить", callback_data=f"set_prayer_offset_{prayer_key}_0")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="offset_per_prayer")
    )
    
    return builder.as_markup()


def schedule_day_keyboard(current: str = "today") -> InlineKeyboardMarkup:
    """Выбор дня для авто-расписания"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=f"{'✅ ' if current == 'today' else ''}Сегодня",
            callback_data="set_day_today"
        ),
        InlineKeyboardButton(
            text=f"{'✅ ' if current == 'tomorrow' else ''}Завтра",
            callback_data="set_day_tomorrow"
        )
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings")
    )
    
    return builder.as_markup()


def reminders_keyboard(enabled_reminders: dict = None, prayer_names_style: str = "standard") -> InlineKeyboardMarkup:
    """Настройка напоминаний"""
    builder = InlineKeyboardBuilder()
    enabled_reminders = enabled_reminders or {}
    prayer_names = get_prayer_names(prayer_names_style)
    
    for prayer_key in PRAYER_KEYS:
        reminder = enabled_reminders.get(prayer_key)
        status = f" ({reminder} мин)" if reminder else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{'✅' if reminder else '⬜'} {prayer_names[prayer_key]}{status}",
                callback_data=f"reminder_{prayer_key}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="🔄 Сбросить все", callback_data="reminder_reset_all")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()


def reminder_time_keyboard(prayer_key: str) -> InlineKeyboardMarkup:
    """Выбор времени напоминания"""
    builder = InlineKeyboardBuilder()
    
    times = [5, 10, 15, 20, 30, 45, 60]
    
    for i in range(0, len(times), 3):
        row_times = times[i:i+3]
        builder.row(*[
            InlineKeyboardButton(
                text=f"{t} мин",
                callback_data=f"set_reminder_{prayer_key}_{t}"
            )
            for t in row_times
        ])
    
    builder.row(
        InlineKeyboardButton(text="❌ Отключить", callback_data=f"set_reminder_{prayer_key}_0")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="reminders")
    )
    
    return builder.as_markup()


def location_keyboard() -> InlineKeyboardMarkup:
    """Выбор локации"""
    builder = InlineKeyboardBuilder()
    
    locations = [
        ("Акъмесджит (Симферополь)", 0),
        ("Алушта", -1),
        ("Багъчасарай", 2),
        ("Къарасувбазар (Белогорск)", -2),
        ("Джанкой", -1),
        ("Кезлев (Евпатория)", 3),
        ("Сакъ (Саки)", 3),
        ("Керич (Керчь)", -9),
        ("Ор Къапы (Перекоп)", 2),
        ("Акъяр (Севастополь)", 2),
        ("Эски Къырым (Старый Крым)", -3),
        ("Кефе (Феодосия)", -5),
        ("Ялта", 4),
        ("Судакъ (Судак)", -3),
        ("Акъшейх (Раздольное)", 3),
        ("Акъмечит (Черноморское)", 4),
    ]
    
    for i in range(0, len(locations), 2):
        row_locs = locations[i:i+2]
        builder.row(*[
            InlineKeyboardButton(
                text=name,
                callback_data=f"set_location_{name}_{offset}"
            )
            for name, offset in row_locs
        ])
    
    builder.row(
        InlineKeyboardButton(text="✏️ Своё смещение", callback_data="manual_offset")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()


def back_to_settings_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад к настройкам"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings")
    )
    return builder.as_markup()


def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    """Подтверждение действия"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}"),
        InlineKeyboardButton(text="❌ Нет", callback_data="main_menu")
    )
    
    return builder.as_markup()