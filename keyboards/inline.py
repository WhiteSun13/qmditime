from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import PRAYER_NAMES_STYLES, PRAYER_KEYS, LOCATIONS


def get_prayer_names(style: str = "standard"):
    return PRAYER_NAMES_STYLES.get(style, PRAYER_NAMES_STYLES["standard"])


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏰ Ежедневная рассылка", callback_data="settings_auto")
    )
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
    """Меню настроек (без локации и смещения времени)"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔤 Язык названий", callback_data="settings_prayer_names")
    )
    builder.row(
        InlineKeyboardButton(text="📅 Дата по Хиджре", callback_data="settings_hijri")
    )
    builder.row(
        InlineKeyboardButton(text="🎉 Праздники", callback_data="settings_holidays")
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
    
    show_text = "✅ Показывать хиджри" if show_hijri else "⬜ Показывать хиджри"
    builder.row(
        InlineKeyboardButton(text=show_text, callback_data="toggle_hijri")
    )
    
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
        InlineKeyboardButton(text="📆 Какой день присылать", callback_data="settings_day")
    )
    builder.row(
        InlineKeyboardButton(text="❌ Отключить", callback_data="set_auto_time_off")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
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
        InlineKeyboardButton(text="◀️ Назад", callback_data="settings_auto")
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


def location_keyboard(current_location: str = "", show_location: bool = True) -> InlineKeyboardMarkup:
    """Выбор локации из главного меню"""
    builder = InlineKeyboardBuilder()
    
    # Toggle показа названия города
    show_text = "✅ Показывать локацию в расписании" if show_location else "⬜ Показывать локацию в расписании"
    builder.row(
        InlineKeyboardButton(text=show_text, callback_data="toggle_location_display")
    )
    
    # Список городов (по 2 в ряд)
    for i in range(0, len(LOCATIONS), 2):
        row_locs = LOCATIONS[i:i+2]
        buttons = []
        for j, (name, offset) in enumerate(row_locs):
            idx = i + j
            prefix = "✅ " if current_location == name else ""
            buttons.append(
                InlineKeyboardButton(
                    text=f"{prefix}{name}",
                    callback_data=f"set_loc_{idx}"
                )
            )
        builder.row(*buttons)
    
    builder.row(
        InlineKeyboardButton(text="🏙 Другая локация", callback_data="custom_location")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
    )
    
    return builder.as_markup()


def custom_location_offset_keyboard() -> InlineKeyboardMarkup:
    """Выбор смещения для другого города"""
    builder = InlineKeyboardBuilder()
    
    offsets = [
        [-10, -5, -3, -2],
        [-1, 0, 1, 2],
        [3, 4, 5, 10]
    ]
    
    for row in offsets:
        builder.row(*[
            InlineKeyboardButton(
                text=f"{offset:+d}" if offset != 0 else "0",
                callback_data=f"custom_offset_{offset}"
            )
            for offset in row
        ])
    
    builder.row(
        InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="custom_offset_manual")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Отмена", callback_data="location")
    )
    
    return builder.as_markup()


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Кнопка назад в главное меню"""
    builder = InlineKeyboardBuilder()
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