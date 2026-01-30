from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import schedule_keyboard, date_navigation_keyboard
from database import get_chat_settings, save_chat_settings
from prayer_times import prayer_manager
from datetime import datetime, timedelta, date
import pytz
from config import TIMEZONE, PRAYER_NAMES_STYLES, ADMIN_ID
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest
from locales import get_text

router = Router()


class ScheduleStates(StatesGroup):
    waiting_custom_date = State()


def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь админом"""
    return user_id in ADMIN_ID


@router.callback_query(F.data == "schedule")
async def show_schedule_menu(callback: CallbackQuery, _: callable, lang: str):
    """Показать меню расписания"""
    text = _("schedule_title")
    
    await callback.message.edit_text(
        text,
        reply_markup=schedule_keyboard(is_admin(callback.from_user.id), lang),
        parse_mode="HTML"
    )
    await callback.answer()


async def get_schedule_text(chat_id: int, target_date: date, lang: str) -> str:
    """Получить текст расписания для даты"""
    settings = await get_chat_settings(chat_id)
    if not settings:
        settings = {}
    
    return prayer_manager.format_schedule(
        target_date=target_date,
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


@router.callback_query(F.data == "schedule_today")
async def schedule_today(callback: CallbackQuery, _: callable, lang: str):
    """Расписание на сегодня"""
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    
    text = await get_schedule_text(callback.message.chat.id, today, lang)
    
    # Игнорируем ошибку, если текст не изменился
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=schedule_keyboard(is_admin(callback.from_user.id), lang),
            parse_mode="HTML"
        )
    
    # answer() должен быть ВНЕ блока suppress, чтобы крутилка на кнопке исчезла
    await callback.answer()


@router.callback_query(F.data == "schedule_tomorrow")
async def schedule_tomorrow(callback: CallbackQuery, _: callable, lang: str):
    """Расписание на завтра"""
    tz = pytz.timezone(TIMEZONE)
    tomorrow = datetime.now(tz).date() + timedelta(days=1)
    
    text = await get_schedule_text(callback.message.chat.id, tomorrow, lang)
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=schedule_keyboard(is_admin(callback.from_user.id), lang),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data == "schedule_custom_date")
async def schedule_custom_date(callback: CallbackQuery, _: callable, lang: str):
    """Показать выбор даты (только для админов)"""
    if not is_admin(callback.from_user.id):
        await callback.answer(_("no_access"), show_alert=True)
        return
    
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    
    text = await get_schedule_text(callback.message.chat.id, today, lang)
    text += f"\n\n<i>{_('use_navigation')}</i>"
    
    await callback.message.edit_text(
        text,
        reply_markup=date_navigation_keyboard(today.isoformat(), lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("date_nav_"))
async def navigate_date(callback: CallbackQuery, _: callable, lang: str):
    """Навигация по датам"""
    if not is_admin(callback.from_user.id):
        await callback.answer(_("no_access"), show_alert=True)
        return
    
    parts = callback.data.replace("date_nav_", "").rsplit("_", 1)
    current_date_str = parts[0]
    offset_days = int(parts[1])
    
    try:
        current_date = date.fromisoformat(current_date_str)
        new_date = current_date + timedelta(days=offset_days)
        
        text = await get_schedule_text(callback.message.chat.id, new_date, lang)
        text += f"\n\n<i>{_('use_navigation')}</i>"
        
        await callback.message.edit_text(
            text,
            reply_markup=date_navigation_keyboard(new_date.isoformat(), lang),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"{_('error')}: {e}", show_alert=True)


@router.callback_query(F.data == "schedule_enter_date")
async def enter_date(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Ввод даты вручную"""
    if not is_admin(callback.from_user.id):
        await callback.answer(_("no_access"), show_alert=True)
        return
    
    text = (
        f"{_('enter_date_title')}\n\n"
        f"{_('enter_date_format')}\n\n"
        f"{_('enter_date_short')}"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(ScheduleStates.waiting_custom_date)
    await state.update_data(lang=lang)
    await callback.answer()


@router.message(ScheduleStates.waiting_custom_date)
async def process_custom_date(message: Message, state: FSMContext):
    """Обработка введённой даты"""
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    
    import re
    
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    _ = lambda key: get_text(lang, key)
    
    text = message.text.strip()
    tz = pytz.timezone(TIMEZONE)
    current_year = datetime.now(tz).year
    
    patterns = [
        (r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', True),
        (r'^(\d{1,2})\.(\d{1,2})$', False),
        (r'^(\d{1,2})/(\d{1,2})/(\d{4})$', True),
        (r'^(\d{1,2})/(\d{1,2})$', False),
        (r'^(\d{1,2})-(\d{1,2})-(\d{4})$', True),
        (r'^(\d{1,2})-(\d{1,2})$', False),
    ]
    
    parsed_date = None
    
    for pattern, has_year in patterns:
        match = re.match(pattern, text)
        if match:
            groups = match.groups()
            day = int(groups[0])
            month = int(groups[1])
            year = int(groups[2]) if has_year else current_year
            
            try:
                parsed_date = date(year, month, day)
                break
            except ValueError:
                pass
    
    if not parsed_date:
        await message.answer(_("date_invalid"))
        return
    
    await state.clear()
    
    schedule_text = await get_schedule_text(message.chat.id, parsed_date, lang)
    schedule_text += f"\n\n<i>{_('use_navigation')}</i>"
    
    await message.answer(
        schedule_text,
        reply_markup=date_navigation_keyboard(parsed_date.isoformat(), lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "next_prayer")
async def next_prayer(callback: CallbackQuery, _: callable, lang: str):
    """Следующий намаз"""
    settings = await get_chat_settings(callback.message.chat.id)
    if not settings:
        settings = {}
    
    prayer_names_style = settings.get('prayer_names_style', 'standard')
    prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES['standard'])
    
    result = prayer_manager.get_next_prayer(
        general_offset=settings.get('time_offset', 0),
        prayer_offsets=settings.get('prayer_offsets', {})
    )
    
    if result:
        prayer_key, time, prayer_date = result
        prayer_name = prayer_names[prayer_key]
        
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
        
        prayer_datetime = datetime.combine(prayer_date, datetime.strptime(time, "%H:%M").time())
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
    
    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text,
            reply_markup=schedule_keyboard(is_admin(callback.from_user.id), lang),
            parse_mode="HTML"
        )
    await callback.answer()