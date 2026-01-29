from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import (
    settings_keyboard, auto_schedule_keyboard,
    schedule_day_keyboard, prayer_names_style_keyboard,
    hijri_settings_keyboard, holidays_settings_keyboard,
    language_keyboard
)
from database import get_chat_settings, save_chat_settings
from locales import get_text

router = Router()


class SettingsStates(StatesGroup):
    waiting_custom_time = State()


async def show_settings_message(message: Message, _: callable, lang: str):
    """Показать настройки как сообщение"""
    settings = await get_chat_settings(message.chat.id)
    
    if not settings:
        await save_chat_settings(message.chat.id, message.chat.type)
        settings = await get_chat_settings(message.chat.id)
    
    auto_time = settings.get('daily_schedule_time') if settings else None
    day = settings.get('schedule_day', 'today') if settings else 'today'
    style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    show_hijri = settings.get('show_hijri', 1) if settings else 1
    show_holidays = settings.get('show_holidays', 1) if settings else 1
    
    style_names = {
        'standard': _('prayer_names_standard').split('(')[0].strip(),
        'crimean_cyrillic': _('prayer_names_cyrillic').split('(')[0].strip(),
        'crimean_latin': _('prayer_names_latin').split('(')[0].strip()
    }
    
    day_text = _("settings_today") if day == 'today' else _("settings_tomorrow")
    auto_text = auto_time if auto_time else _("settings_disabled")
    
    text = (
        f"{_('settings_title')}\n\n"
        f"{_('settings_mailing')} <b>{auto_text}</b>\n"
        f"{_('settings_mailing_day')} <b>{day_text}</b>\n"
        f"{_('settings_prayer_style')} <b>{style_names.get(style, style_names['standard'])}</b>\n"
        f"{_('settings_hijri')} <b>{_('settings_on') if show_hijri else _('settings_off')}</b>\n"
        f"{_('settings_holidays')} <b>{_('settings_on') if show_holidays else _('settings_off')}</b>\n"
    )
    
    await message.answer(text, reply_markup=settings_keyboard(lang), parse_mode="HTML")


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, _: callable, lang: str):
    """Показать настройки"""
    settings = await get_chat_settings(callback.message.chat.id)
    
    auto_time = settings.get('daily_schedule_time') if settings else None
    day = settings.get('schedule_day', 'today') if settings else 'today'
    style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    show_hijri = settings.get('show_hijri', 1) if settings else 1
    show_holidays = settings.get('show_holidays', 1) if settings else 1
    
    style_names = {
        'standard': _('prayer_names_standard').split('(')[0].strip(),
        'crimean_cyrillic': _('prayer_names_cyrillic').split('(')[0].strip(),
        'crimean_latin': _('prayer_names_latin').split('(')[0].strip()
    }
    
    day_text = _("settings_today") if day == 'today' else _("settings_tomorrow")
    auto_text = auto_time if auto_time else _("settings_disabled")
    
    text = (
        f"{_('settings_title')}\n\n"
        f"{_('settings_mailing')} <b>{auto_text}</b>\n"
        f"{_('settings_mailing_day')} <b>{day_text}</b>\n"
        f"{_('settings_prayer_style')} <b>{style_names.get(style, style_names['standard'])}</b>\n"
        f"{_('settings_hijri')} <b>{_('settings_on') if show_hijri else _('settings_off')}</b>\n"
        f"{_('settings_holidays')} <b>{_('settings_on') if show_holidays else _('settings_off')}</b>\n"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=settings_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


# === Названия намазов ===

@router.callback_query(F.data == "settings_prayer_names")
async def settings_prayer_names(callback: CallbackQuery, _: callable, lang: str):
    """Настройка названий намазов"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    
    text = _("prayer_names_title")
    
    await callback.message.edit_text(
        text,
        reply_markup=prayer_names_style_keyboard(current, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_prayer_style_"))
async def set_prayer_style(callback: CallbackQuery, _: callable, lang: str):
    """Установка стиля названий"""
    style = callback.data.replace("set_prayer_style_", "")
    await save_chat_settings(callback.message.chat.id, prayer_names_style=style)
    await callback.answer(_("style_changed"))
    await settings_prayer_names(callback, _, lang)


# === Настройки хиджри ===

@router.callback_query(F.data == "settings_hijri")
async def settings_hijri(callback: CallbackQuery, _: callable, lang: str):
    """Настройки хиджри"""
    settings = await get_chat_settings(callback.message.chat.id)
    show_hijri = bool(settings.get('show_hijri', 1)) if settings else True
    hijri_style = settings.get('hijri_style', 'translit') if settings else 'translit'
    
    # Определяем какой транслит будет использоваться
    if hijri_style == 'translit':
        if lang == 'crh_lat':
            translit_type = _('hijri_latin')
        else:
            translit_type = _('hijri_cyrillic')
        style_display = f"{_('hijri_translit')} ({translit_type})"
    else:
        style_display = _('hijri_arabic')
    
    # Пример в зависимости от стиля
    if hijri_style == 'arabic':
        example = _('hijri_example_arabic')
    else:
        example = _('hijri_example_translit')
    
    text = (
        f"{_('hijri_title')}\n\n"
        f"{_('hijri_show')} <b>{_('hijri_yes') if show_hijri else _('hijri_no')}</b>\n"
        f"{_('hijri_style')} <b>{style_display}</b>\n\n"
        f"{_('hijri_example')} {example}"
    )
    
    if hijri_style == 'translit':
        text += f"\n\n<i>ℹ️ {_('hijri_translit_auto')}</i>"
    
    await callback.message.edit_text(
        text,
        reply_markup=hijri_settings_keyboard(show_hijri, hijri_style, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_hijri")
async def toggle_hijri(callback: CallbackQuery, _: callable, lang: str):
    """Переключение отображения хиджри"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = bool(settings.get('show_hijri', 1)) if settings else True
    await save_chat_settings(callback.message.chat.id, show_hijri=0 if current else 1)
    await callback.answer(_("changed"))
    await settings_hijri(callback, _, lang)


@router.callback_query(F.data.startswith("set_hijri_style_"))
async def set_hijri_style(callback: CallbackQuery, _: callable, lang: str):
    """Установка стиля хиджри (arabic или translit)"""
    style = callback.data.replace("set_hijri_style_", "")
    await save_chat_settings(callback.message.chat.id, hijri_style=style)
    await callback.answer(_("style_changed"))
    await settings_hijri(callback, _, lang)


# === Настройки праздников ===

@router.callback_query(F.data == "settings_holidays")
async def settings_holidays(callback: CallbackQuery, _: callable, lang: str):
    """Настройки праздников"""
    settings = await get_chat_settings(callback.message.chat.id)
    show_holidays = bool(settings.get('show_holidays', 1)) if settings else True
    
    text = (
        f"{_('holidays_settings_title')}\n\n"
        f"{_('holidays_show')} <b>{_('hijri_yes') if show_holidays else _('hijri_no')}</b>\n\n"
        f"{_('holidays_when_enabled')}\n"
        f"• {_('holidays_feature_1')}\n"
        f"• {_('holidays_feature_2')}\n"
        f"• {_('holidays_feature_3')}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=holidays_settings_keyboard(show_holidays, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_holidays")
async def toggle_holidays(callback: CallbackQuery, _: callable, lang: str):
    """Переключение отображения праздников"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = bool(settings.get('show_holidays', 1)) if settings else True
    await save_chat_settings(callback.message.chat.id, show_holidays=0 if current else 1)
    await callback.answer(_("changed"))
    await settings_holidays(callback, _, lang)


@router.callback_query(F.data == "holidays_list")
async def holidays_list(callback: CallbackQuery, _: callable, lang: str):
    """Переход к списку праздников"""
    from handlers.start import show_holidays
    await show_holidays(callback, _, lang)


# === Авто-расписание ===

@router.callback_query(F.data == "settings_auto")
async def settings_auto(callback: CallbackQuery, _: callable, lang: str):
    """Настройка авто-расписания"""
    settings = await get_chat_settings(callback.message.chat.id)
    current_time = settings.get('daily_schedule_time') if settings else None
    
    text = (
        f"{_('auto_schedule_title')}\n\n"
        f"{_('auto_current_time')} <b>{current_time or _('auto_not_set')}</b>"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=auto_schedule_keyboard(current_time, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_auto_time_"))
async def set_auto_time(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Установка времени авто-расписания"""
    time_value = callback.data.replace("set_auto_time_", "")
    
    if time_value == "custom":
        await callback.message.edit_text(
            _("enter_time"),
            parse_mode="HTML"
        )
        await state.set_state(SettingsStates.waiting_custom_time)
        await state.update_data(lang=lang)
        await callback.answer()
        return
    
    if time_value == "off":
        await save_chat_settings(callback.message.chat.id, daily_schedule_time=None)
        await callback.answer(_("auto_disabled"))
    else:
        await save_chat_settings(callback.message.chat.id, daily_schedule_time=time_value)
        await callback.answer(f"{_('auto_set')} {time_value}")
    
    await settings_auto(callback, _, lang)


@router.message(SettingsStates.waiting_custom_time)
async def process_custom_time(message: Message, state: FSMContext):
    """Обработка пользовательского времени"""
    import re
    
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    _ = lambda key: get_text(lang, key)
    
    time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$')
    
    if time_pattern.match(message.text):
        await save_chat_settings(message.chat.id, daily_schedule_time=message.text)
        await state.clear()
        await message.answer(
            f"{_('time_set')} {message.text}\n\n"
            f"{_('use_start_menu')}"
        )
    else:
        await message.answer(_("time_invalid"))


# === День расписания ===

@router.callback_query(F.data == "settings_day")
async def settings_day(callback: CallbackQuery, _: callable, lang: str):
    """Настройка дня расписания"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = settings.get('schedule_day', 'today') if settings else 'today'
    
    text = (
        f"{_('day_title')}\n\n"
        f"{_('day_current')} <b>{_('day_today_schedule') if current == 'today' else _('day_tomorrow_schedule')}</b>"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=schedule_day_keyboard(current, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_day_"))
async def set_day(callback: CallbackQuery, _: callable, lang: str):
    """Установка дня"""
    day = callback.data.replace("set_day_", "")
    await save_chat_settings(callback.message.chat.id, schedule_day=day)
    await callback.answer(_("day_set_today") if day == 'today' else _("day_set_tomorrow"))
    await settings_day(callback, _, lang)


# Меню выбора языка
@router.callback_query(F.data == "settings_language")
async def show_language_menu(callback: CallbackQuery, _: callable, lang: str):
    text = _("language_select")
    await callback.message.edit_text(text, reply_markup=language_keyboard(lang), parse_mode="HTML")
    await callback.answer()


# Обработка выбора языка
@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery):
    # Тут мы не можем использовать injected _, так как язык меняется на лету
    # Поэтому берем новый код языка
    new_lang = callback.data.replace("set_lang_", "")
    
    # Сохраняем в БД
    await save_chat_settings(callback.message.chat.id, language=new_lang)
    
    prayer_style = "standard"
    if new_lang == "crh_lat":
        prayer_style = "crimean_latin"
    elif new_lang == "crh_cyr":
        prayer_style = "crimean_cyrillic"
        
    await save_chat_settings(callback.message.chat.id, prayer_names_style=prayer_style)
    
    text = get_text(new_lang, "changed_lang")
    await callback.answer(text)
    
    # Создаём новую функцию перевода для нового языка
    new_ = lambda key: get_text(new_lang, key)
    
    settings_text = get_text(new_lang, "settings_title")
    
    # Тут нужно обновить функцию settings_keyboard, чтобы она принимала lang
    await callback.message.edit_text(
        settings_text, 
        reply_markup=settings_keyboard(lang=new_lang),
        parse_mode="HTML"
    )