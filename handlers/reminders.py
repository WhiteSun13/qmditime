from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline import reminders_keyboard, reminder_time_keyboard
from database import get_chat_settings, save_chat_settings
from config import PRAYER_NAMES_STYLES

router = Router()


@router.callback_query(F.data == "reminders")
async def show_reminders(callback: CallbackQuery, _: callable, lang: str):
    """Показать настройки напоминаний"""
    settings = await get_chat_settings(callback.message.chat.id)
    reminders = settings.get('reminders', {}) if settings else {}
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    
    text = _("reminders_title")
    
    await callback.message.edit_text(
        text,
        reply_markup=reminders_keyboard(reminders, prayer_names_style, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reminder_") & ~F.data.startswith("reminder_reset"))
async def select_reminder(callback: CallbackQuery, _: callable, lang: str):
    """Выбор намаза для напоминания"""
    prayer_key = callback.data.replace("reminder_", "")
    
    settings = await get_chat_settings(callback.message.chat.id)
    reminders = settings.get('reminders', {}) if settings else {}
    current = reminders.get(prayer_key, 0)
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES['standard'])
    
    text = (
        f"{_('reminder_for').format(prayer=prayer_names[prayer_key])}\n\n"
        f"{_('reminder_current')} <b>{current} {_('minutes')}</b> {_('reminder_before')}\n\n"
        f"{_('reminder_select_time')}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=reminder_time_keyboard(prayer_key, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_reminder_"))
async def set_reminder(callback: CallbackQuery, _: callable, lang: str):
    """Установка напоминания"""
    parts = callback.data.replace("set_reminder_", "").rsplit("_", 1)
    prayer_key = parts[0]
    minutes = int(parts[1])
    
    settings = await get_chat_settings(callback.message.chat.id)
    reminders = settings.get('reminders', {}) if settings else {}
    
    if minutes == 0:
        reminders.pop(prayer_key, None)
        await callback.answer(_("reminder_disabled"))
    else:
        reminders[prayer_key] = minutes
        await callback.answer(_("reminder_set").format(min=minutes))
    
    await save_chat_settings(callback.message.chat.id, reminders=reminders)
    await show_reminders(callback, _, lang)


@router.callback_query(F.data == "reminder_reset_all")
async def reset_all_reminders(callback: CallbackQuery, _: callable, lang: str):
    """Сброс всех напоминаний"""
    await save_chat_settings(callback.message.chat.id, reminders={})
    await callback.answer(_("all_reminders_reset"))
    await show_reminders(callback, _, lang)