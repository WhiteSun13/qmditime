from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline import reminders_keyboard, reminder_time_keyboard
from database import get_chat_settings, save_chat_settings
from config import PRAYER_NAMES_STYLES

router = Router()


@router.callback_query(F.data == "reminders")
async def show_reminders(callback: CallbackQuery):
    """Показать настройки напоминаний"""
    settings = await get_chat_settings(callback.message.chat.id)
    reminders = settings.get('reminders', {}) if settings else {}
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    
    text = (
        "🔔 <b>Напоминания</b>\n\n"
        "Настройте уведомления перед намазом.\n"
        "Выберите намаз для настройки:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=reminders_keyboard(reminders, prayer_names_style),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reminder_") & ~F.data.startswith("reminder_reset"))
async def select_reminder(callback: CallbackQuery):
    """Выбор намаза для напоминания"""
    prayer_key = callback.data.replace("reminder_", "")
    
    settings = await get_chat_settings(callback.message.chat.id)
    reminders = settings.get('reminders', {}) if settings else {}
    current = reminders.get(prayer_key, 0)
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES['standard'])
    
    text = (
        f"🔔 <b>Напоминание для {prayer_names[prayer_key]}</b>\n\n"
        f"Текущее: <b>{current} мин</b> до намаза\n\n"
        "Выберите за сколько минут напоминать:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=reminder_time_keyboard(prayer_key),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_reminder_"))
async def set_reminder(callback: CallbackQuery):
    """Установка напоминания"""
    parts = callback.data.replace("set_reminder_", "").rsplit("_", 1)
    prayer_key = parts[0]
    minutes = int(parts[1])
    
    settings = await get_chat_settings(callback.message.chat.id)
    reminders = settings.get('reminders', {}) if settings else {}
    
    if minutes == 0:
        reminders.pop(prayer_key, None)
        await callback.answer(f"✅ Напоминание отключено")
    else:
        reminders[prayer_key] = minutes
        await callback.answer(f"✅ Напоминание за {minutes} мин")
    
    await save_chat_settings(callback.message.chat.id, reminders=reminders)
    await show_reminders(callback)


@router.callback_query(F.data == "reminder_reset_all")
async def reset_all_reminders(callback: CallbackQuery):
    """Сброс всех напоминаний"""
    await save_chat_settings(callback.message.chat.id, reminders={})
    await callback.answer("✅ Все напоминания отключены")
    await show_reminders(callback)