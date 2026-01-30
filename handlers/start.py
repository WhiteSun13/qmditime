from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from keyboards.inline import main_menu_keyboard, schedule_keyboard, help_keyboard
from database import save_chat_settings, get_chat_settings
from prayer_times import prayer_manager
from datetime import datetime, timedelta, date
import pytz
from config import TIMEZONE, PRAYER_NAMES_STYLES, HOLIDAYS, ADMIN_ID
from locales import get_text, get_month

def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь админом"""
    return user_id in ADMIN_ID


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, _: callable, lang: str): 
    await save_chat_settings(
        chat_id=message.chat.id,
        chat_type=message.chat.type,
        is_active=1 
    )
    
    text = _("main_menu_title")
    await message.answer(text, reply_markup=main_menu_keyboard(lang), parse_mode="HTML")


@router.message(Command("settings"))
async def cmd_settings(message: Message, _: callable, lang: str):
    """Команда /settings"""
    from handlers.settings import show_settings_message
    await show_settings_message(message, _, lang)


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, _: callable, lang: str):
    """Возврат в главное меню"""
    text = _("main_menu_title")
    
    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery, _: callable, lang: str):
    """Показать помощь"""
    text = (
        f"{_('help_title')}\n\n"
        f"{_('help_commands')}\n"
        f"{_('help_cmd_start')}\n"
        f"{_('help_cmd_schedule')}\n"
        f"{_('help_cmd_tomorrow')}\n"
        f"{_('help_cmd_next')}\n"
        f"{_('help_cmd_settings')}\n"
        f"{_('help_cmd_holidays')}\n\n"
        f"{_('help_settings_title')}\n"
        f"{_('help_setting_mailing')}\n"
        f"{_('help_setting_offset')}\n"
        f"{_('help_setting_hijri')}\n"
        f"{_('help_setting_holidays')}\n"
        f"{_('help_setting_reminders')}\n\n"
        f"{_('help_groups')}"
    )
    
    await callback.message.edit_text(text, reply_markup=help_keyboard(lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "holidays")
async def show_holidays(callback: CallbackQuery, _: callable, lang: str):
    """Показать список праздников"""
    tz = pytz.timezone(TIMEZONE)
    current_year = datetime.now(tz).year
    
    year_holidays = HOLIDAYS.get(current_year, {})
    
    if not year_holidays:
        text = _("holidays_not_found").format(year=current_year)
    else:
        text = f"🎉 <b>{_('holidays_title')} {current_year}</b>\n"
        
        # Группируем по месяцам
        by_month = {}
        for (month, day), info in sorted(year_holidays.items()):
            if month not in by_month:
                by_month[month] = []
            by_month[month].append((day, info))
        
        for month in sorted(by_month.keys()):
            text += f"\n<b>{get_month(lang, month, header=True)}</b>\n"
            for day, info in by_month[month]:
                emoji = "🌟" if info["type"] == "holiday" else "✨" if info.get("night") else "📿"
                if info.get("night"):
                    # Ночь с предыдущего на указанный день
                    try:
                        current_date = date(current_year, month, day)
                        prev_date = current_date - timedelta(days=1)
                        if prev_date.month == month:
                            text += f"  {prev_date.day}-{day}: {emoji} {info['name']}\n"
                        else:
                            text += f"  {prev_date.day} {get_month(lang, prev_date.month, header=True)}-{day}: {emoji} {info['name']}\n"
                    except:
                        text += f"  {day}: {emoji} {info['name']}\n"
                else:
                    text += f"  {day}: {emoji} {info['name']}\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=_("btn_back"), callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.message(Command("holidays"))
async def cmd_holidays(message: Message, _: callable, lang: str):
    """Команда /holidays"""
    tz = pytz.timezone(TIMEZONE)
    current_year = datetime.now(tz).year
    
    year_holidays = HOLIDAYS.get(current_year, {})
    
    if not year_holidays:
        text = _("holidays_not_found").format(year=current_year)
    else:
        text = f"🎉 <b>{_('holidays_title')} {current_year}</b>\n"
        
        by_month = {}
        for (month, day), info in sorted(year_holidays.items()):
            if month not in by_month:
                by_month[month] = []
            by_month[month].append((day, info))
        
        for month in sorted(by_month.keys()):
            text += f"\n<b>{get_month(lang, month, header=True)}</b>\n"
            for day, info in by_month[month]:
                emoji = "🌟" if info["type"] == "holiday" else "✨" if info.get("night") else "📿"
                if info.get("night"):
                    try:
                        current_date = date(current_year, month, day)
                        prev_date = current_date - timedelta(days=1)
                        if prev_date.month == month:
                            text += f"  {prev_date.day}-{day}: {emoji} {info['name']}\n"
                        else:
                            text += f"  {prev_date.day} {get_month(lang, prev_date.month, header=True)}-{day}: {emoji} {info['name']}\n"
                    except:
                        text += f"  {day}: {emoji} {info['name']}\n"
                else:
                    text += f"  {day}: {emoji} {info['name']}\n"
    
    await message.answer(text, parse_mode="HTML")


@router.message(Command("schedule"))
async def cmd_schedule(message: Message, _: callable, lang: str):
    """Команда /schedule - расписание на сегодня"""
    settings = await get_chat_settings(message.chat.id)
    if not settings:
        await save_chat_settings(message.chat.id, message.chat.type)
        settings = await get_chat_settings(message.chat.id)
    
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    
    text = prayer_manager.format_schedule(
        target_date=today,
        general_offset=settings.get('time_offset', 0),
        prayer_offsets=settings.get('prayer_offsets', {}),
        location_name=settings.get('location_name', 'Симферополь'),
        enabled_prayers=settings.get('enabled_prayers'),
        show_location=bool(settings.get('show_location', 1)),
        prayer_names_style=settings.get('prayer_names_style', 'standard'),
        show_hijri=bool(settings.get('show_hijri', 1)),
        hijri_style=settings.get('hijri_style', 'translit'),
        show_holidays=bool(settings.get('show_holidays', 1)),
        lang=lang
    )
    
    await message.answer(
        text,
        reply_markup=schedule_keyboard(is_admin(message.from_user.id), lang),
        parse_mode="HTML"
    )


@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message, _: callable, lang: str):
    """Команда /tomorrow - расписание на завтра"""
    settings = await get_chat_settings(message.chat.id)
    if not settings:
        await save_chat_settings(message.chat.id, message.chat.type)
        settings = await get_chat_settings(message.chat.id)
    
    tz = pytz.timezone(TIMEZONE)
    tomorrow = datetime.now(tz).date() + timedelta(days=1)
    
    text = prayer_manager.format_schedule(
        target_date=tomorrow,
        general_offset=settings.get('time_offset', 0),
        prayer_offsets=settings.get('prayer_offsets', {}),
        location_name=settings.get('location_name', 'Симферополь'),
        enabled_prayers=settings.get('enabled_prayers'),
        show_location=bool(settings.get('show_location', 1)),
        prayer_names_style=settings.get('prayer_names_style', 'standard'),
        show_hijri=bool(settings.get('show_hijri', 1)),
        hijri_style=settings.get('hijri_style', 'translit'),
        show_holidays=bool(settings.get('show_holidays', 1)),
        lang=lang
    )
    
    await message.answer(
        text,
        reply_markup=schedule_keyboard(is_admin(message.from_user.id), lang),
        parse_mode="HTML"
    )


@router.message(Command("next"))
async def cmd_next(message: Message, _: callable, lang: str):
    """Команда /next - следующий намаз"""
    settings = await get_chat_settings(message.chat.id)
    if not settings:
        await save_chat_settings(message.chat.id, message.chat.type)
        settings = await get_chat_settings(message.chat.id)
    
    prayer_names = PRAYER_NAMES_STYLES.get(
        settings.get('prayer_names_style', 'standard'),
        PRAYER_NAMES_STYLES['standard']
    )
    
    result = prayer_manager.get_next_prayer(
        general_offset=settings.get('time_offset', 0),
        prayer_offsets=settings.get('prayer_offsets', {})
    )
    
    if result:
        prayer_key, time, date = result
        prayer_name = prayer_names[prayer_key]
        
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
        
        prayer_datetime = datetime.combine(date, datetime.strptime(time, "%H:%M").time())
        prayer_datetime = tz.localize(prayer_datetime)
        
        diff = prayer_datetime - now
        hours, remainder = divmod(int(diff.total_seconds()), 3600)
        minutes, secs = divmod(remainder, 60)
        
        if hours > 0:
            remaining = f"{hours} {_('hour_short')} {minutes} {_('min_short')}"
        else:
            remaining = f"{minutes} {_('min_short')}"
        
        text = (
            f"{_('next_prayer_title')}\n\n"
            f"{prayer_name}\n"
            f"{_('next_prayer_time')} <b>{time}</b>\n"
            f"{_('next_prayer_remaining')} <b>{remaining}</b>"
        )
    else:
        text = _("next_prayer_error")
    
    await message.answer(
        text,
        reply_markup=schedule_keyboard(is_admin(message.from_user.id), lang),
        parse_mode="HTML"
    )


@router.message(Command("reload"))
async def cmd_reload(message: Message, _: callable, lang: str):
    """Перезагрузка данных CSV (только для админов)"""
    if message.from_user.id not in ADMIN_ID:
        await message.answer(_("no_access"))
        return
    
    try:
        prayer_manager.load_data()
        rows = len(prayer_manager.df)
        await message.answer(f"✅ Данные перезагружены\n📊 Загружено {rows} дней")
    except Exception as e:
        await message.answer(f"{_('error')}: {e}")


@router.message(Command("export"))
async def cmd_export(message: Message, _: callable, lang: str):
    """Экспорт базы данных (только для админов)"""
    if message.from_user.id not in ADMIN_ID:
        await message.answer(_("no_access"))
        return
    
    from config import DATABASE_PATH
    import os
    
    if not os.path.exists(DATABASE_PATH):
        await message.answer(f"{_('error')}: База не найдена")
        return
    
    try:
        file = FSInputFile(DATABASE_PATH, filename="prayer_bot_backup.db")
        await message.answer_document(
            file,
            caption=f"📦 <b>Экспорт базы данных</b>\n\n"
                    f"📅 Дата: {datetime.now(pytz.timezone(TIMEZONE)).strftime('%d.%m.%Y %H:%M')}",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(f"{_('error')}: {e}")