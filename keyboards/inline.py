from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import PRAYER_NAMES_STYLES, PRAYER_KEYS, LOCATIONS
from locales import get_text


def get_prayer_names(style: str = "standard"):
    return PRAYER_NAMES_STYLES.get(style, PRAYER_NAMES_STYLES["standard"])


def main_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Главное меню"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=_("btn_auto_schedule"), callback_data="settings_auto")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_schedule"), callback_data="schedule"),
        InlineKeyboardButton(text=_("btn_reminders"), callback_data="reminders")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_holidays"), callback_data="holidays"),
        InlineKeyboardButton(text=_("btn_location"), callback_data="location")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_settings"), callback_data="settings"),
        InlineKeyboardButton(text=_("btn_help"), callback_data="help")
    )
    
    return builder.as_markup()


def schedule_keyboard(is_admin: bool = False, lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню расписания"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=_("btn_today"), callback_data="schedule_today"),
        InlineKeyboardButton(text=_("btn_tomorrow"), callback_data="schedule_tomorrow")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_next_prayer"), callback_data="next_prayer")
    )
    
    if is_admin:
        builder.row(
            InlineKeyboardButton(text=_("btn_select_date"), callback_data="schedule_custom_date")
        )
    
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="main_menu")
    )
    
    return builder.as_markup()


def date_navigation_keyboard(current_date: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Навигация по датам"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="◀️ -7", callback_data=f"date_nav_{current_date}_-7"),
        InlineKeyboardButton(text="◀️ -1", callback_data=f"date_nav_{current_date}_-1"),
        InlineKeyboardButton(text="+1 ▶️", callback_data=f"date_nav_{current_date}_+1"),
        InlineKeyboardButton(text="+7 ▶️", callback_data=f"date_nav_{current_date}_+7"),
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_today"), callback_data="schedule_today"),
        InlineKeyboardButton(text="✏️ Ввести дату", callback_data="schedule_enter_date")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="schedule")
    )
    
    return builder.as_markup()


def settings_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню настроек"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=_("btn_prayer_names"), callback_data="settings_prayer_names")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_hijri"), callback_data="settings_hijri")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_holidays_settings"), callback_data="settings_holidays")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_language"), callback_data="settings_language")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="main_menu")
    )
    
    return builder.as_markup()


def prayer_names_style_keyboard(current: str = "standard", lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор стиля названий намазов"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    styles = [
        ("standard", _("prayer_names_standard")),
        ("crimean_cyrillic", _("prayer_names_cyrillic")),
        ("crimean_latin", _("prayer_names_latin"))
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
        InlineKeyboardButton(text=_("btn_back"), callback_data="settings")
    )
    
    return builder.as_markup()


def hijri_settings_keyboard(show_hijri: bool = True, style: str = "cyrillic", lang: str = "ru") -> InlineKeyboardMarkup:
    """Настройки хиджри"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    show_text = f"{'✅' if show_hijri else '⬜'} {_('btn_show_hijri')}"
    builder.row(
        InlineKeyboardButton(text=show_text, callback_data="toggle_hijri")
    )
    
    builder.row(
        InlineKeyboardButton(
            text=f"{'✅' if style == 'cyrillic' else '⬜'} {_('btn_cyrillic')}",
            callback_data="set_hijri_style_cyrillic"
        ),
        InlineKeyboardButton(
            text=f"{'✅' if style == 'latin' else '⬜'} {_('btn_latin')}",
            callback_data="set_hijri_style_latin"
        )
    )
    
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="settings")
    )
    
    return builder.as_markup()


def holidays_settings_keyboard(show_holidays: bool = True, lang: str = "ru") -> InlineKeyboardMarkup:
    """Настройки праздников"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    show_text = f"{'✅' if show_holidays else '⬜'} {_('btn_show_holidays')}"
    builder.row(
        InlineKeyboardButton(text=show_text, callback_data="toggle_holidays")
    )
    
    builder.row(
        InlineKeyboardButton(text=_("btn_holidays_list"), callback_data="holidays_list")
    )
    
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="settings")
    )
    
    return builder.as_markup()


def auto_schedule_keyboard(current_time: str = None, lang: str = "ru") -> InlineKeyboardMarkup:
    """Настройка авто-расписания"""
    _ = lambda key: get_text(lang, key)
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
        InlineKeyboardButton(text=_("btn_custom_time"), callback_data="set_auto_time_custom")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_which_day"), callback_data="settings_day")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_disable"), callback_data="set_auto_time_off")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="main_menu")
    )
    
    return builder.as_markup()


def schedule_day_keyboard(current: str = "today", lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор дня для авто-расписания"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=f"{'✅ ' if current == 'today' else ''}{_('settings_today').capitalize()}",
            callback_data="set_day_today"
        ),
        InlineKeyboardButton(
            text=f"{'✅ ' if current == 'tomorrow' else ''}{_('settings_tomorrow').capitalize()}",
            callback_data="set_day_tomorrow"
        )
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="settings_auto")
    )
    
    return builder.as_markup()


def reminders_keyboard(enabled_reminders: dict = None, prayer_names_style: str = "standard", lang: str = "ru") -> InlineKeyboardMarkup:
    """Настройка напоминаний"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    enabled_reminders = enabled_reminders or {}
    prayer_names = get_prayer_names(prayer_names_style)
    
    for prayer_key in PRAYER_KEYS:
        reminder = enabled_reminders.get(prayer_key)
        status = f" ({reminder} {_('minutes')})" if reminder else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{'✅' if reminder else '⬜'} {prayer_names[prayer_key]}{status}",
                callback_data=f"reminder_{prayer_key}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text=_("btn_reset_all"), callback_data="reminder_reset_all")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="main_menu")
    )
    
    return builder.as_markup()


def reminder_time_keyboard(prayer_key: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор времени напоминания"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    times = [5, 10, 15, 20, 30, 45, 60]
    
    for i in range(0, len(times), 3):
        row_times = times[i:i+3]
        builder.row(*[
            InlineKeyboardButton(
                text=f"{t} {_('minutes')}",
                callback_data=f"set_reminder_{prayer_key}_{t}"
            )
            for t in row_times
        ])
    
    builder.row(
        InlineKeyboardButton(text=_("btn_disable"), callback_data=f"set_reminder_{prayer_key}_0")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="reminders")
    )
    
    return builder.as_markup()


def location_keyboard(current_location: str = "", show_location: bool = True, lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор локации"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    show_text = f"{'✅' if show_location else '⬜'} {_('btn_show_location')}"
    builder.row(
        InlineKeyboardButton(text=show_text, callback_data="toggle_location_display")
    )
    
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
        InlineKeyboardButton(text=_("btn_other_location"), callback_data="custom_location")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="main_menu")
    )
    
    return builder.as_markup()


def custom_location_menu_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню 'Другой город'"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=_("btn_enter_name"), callback_data="enter_city_name")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_time_offset"), callback_data="offset_menu")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="location")
    )
    
    return builder.as_markup()


def offset_menu_keyboard(general_offset: int = 0, has_prayer_offsets: bool = False, lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню смещения времени"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=f"{_('btn_general_offset')} ({general_offset:+d} {_('minutes')})",
            callback_data="offset_general"
        )
    )
    
    prayer_text = _("btn_by_prayer") + (" ✓" if has_prayer_offsets else "")
    builder.row(
        InlineKeyboardButton(text=prayer_text, callback_data="offset_by_prayer")
    )
    
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="custom_location")
    )
    
    return builder.as_markup()


def general_offset_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор общего смещения"""
    _ = lambda key: get_text(lang, key)
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
                callback_data=f"set_general_offset_{offset}"
            )
            for offset in row
        ])
    
    builder.row(
        InlineKeyboardButton(text=_("btn_enter_manual"), callback_data="general_offset_manual")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="offset_menu")
    )
    
    return builder.as_markup()


def prayer_offsets_keyboard(prayer_offsets: dict = None, prayer_names_style: str = "standard", lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор намаза для настройки смещения"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    prayer_offsets = prayer_offsets or {}
    prayer_names = get_prayer_names(prayer_names_style)
    
    for prayer_key in PRAYER_KEYS:
        offset = prayer_offsets.get(prayer_key, 0)
        offset_text = f" ({offset:+d})" if offset != 0 else ""
        builder.row(
            InlineKeyboardButton(
                text=f"{prayer_names[prayer_key]}{offset_text}",
                callback_data=f"prayer_offset_{prayer_key}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text=_("btn_reset_all"), callback_data="prayer_offset_reset_all")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="offset_menu")
    )
    
    return builder.as_markup()


def prayer_offset_values_keyboard(prayer_key: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Выбор значения смещения для намаза"""
    _ = lambda key: get_text(lang, key)
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
                callback_data=f"set_prayer_offset_{prayer_key}_{offset}"
            )
            for offset in row
        ])
    
    builder.row(
        InlineKeyboardButton(text=_("btn_enter_manual"), callback_data=f"prayer_offset_manual_{prayer_key}")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="offset_by_prayer")
    )
    
    return builder.as_markup()


def back_to_main_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка назад в главное меню"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="main_menu")
    )
    return builder.as_markup()


def back_to_settings_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка назад к настройкам"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="settings")
    )
    return builder.as_markup()


def cancel_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка отмены"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=_("btn_cancel"), callback_data="cancel_feedback")
    )
    return builder.as_markup()


def help_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню раздела Помощь"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text=_("btn_write_developer"), callback_data="feedback")
    )
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="main_menu")
    )
    
    return builder.as_markup()


def language_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    _ = lambda key: get_text(lang, key)
    builder = InlineKeyboardBuilder()
    
    langs = [
        ("ru", "lang_ru"),
        ("crh_cyr", "lang_crh_cyr"),
        ("crh_lat", "lang_crh_lat")
    ]
    
    for code, key in langs:
        prefix = "✅ " if code == lang else ""
        builder.row(
            InlineKeyboardButton(
                text=prefix + _(key),
                callback_data=f"set_lang_{code}"
            )
        )
        
    builder.row(
        InlineKeyboardButton(text=_("btn_back"), callback_data="settings")
    )
    return builder.as_markup()