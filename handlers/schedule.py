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

router = Router()


class ScheduleStates(StatesGroup):
    waiting_custom_date = State()


def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь админом"""
    return user_id in ADMIN_ID


@router.callback_query(F.data == "schedule")
async def show_schedule_menu(callback: CallbackQuery):
    """Показать меню расписания"""
    text = (
        "📅 <b>Расписание намаза</b>\n\n"
        "Выберите день:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=schedule_keyboard(is_admin(callback.from_user.id)),
        parse_mode="HTML"
    )
    await callback.answer()


async def get_schedule_text(chat_id: int, target_date: date) -> str:
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
        hijri_style=settings.get('hijri_style', 'cyrillic'),
        show_holidays=bool(settings.get('show_holidays', 1))
    )


@router.callback_query(F.data == "schedule_today")
async def schedule_today(callback: CallbackQuery):
    """Расписание на сегодня"""
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    
    text = await get_schedule_text(callback.message.chat.id, today)
    
    await callback.message.edit_text(
        text,
        reply_markup=schedule_keyboard(is_admin(callback.from_user.id)),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "schedule_tomorrow")
async def schedule_tomorrow(callback: CallbackQuery):
    """Расписание на завтра"""
    tz = pytz.timezone(TIMEZONE)
    tomorrow = datetime.now(tz).date() + timedelta(days=1)
    
    text = await get_schedule_text(callback.message.chat.id, tomorrow)
    
    await callback.message.edit_text(
        text,
        reply_markup=schedule_keyboard(is_admin(callback.from_user.id)),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "schedule_custom_date")
async def schedule_custom_date(callback: CallbackQuery):
    """Показать выбор даты (только для админов)"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    
    text = await get_schedule_text(callback.message.chat.id, today)
    text += "\n\n<i>Используйте кнопки для навигации по датам</i>"
    
    await callback.message.edit_text(
        text,
        reply_markup=date_navigation_keyboard(today.isoformat()),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("date_nav_"))
async def navigate_date(callback: CallbackQuery):
    """Навигация по датам"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    parts = callback.data.replace("date_nav_", "").rsplit("_", 1)
    current_date_str = parts[0]
    offset_days = int(parts[1])
    
    try:
        current_date = date.fromisoformat(current_date_str)
        new_date = current_date + timedelta(days=offset_days)
        
        text = await get_schedule_text(callback.message.chat.id, new_date)
        text += "\n\n<i>Используйте кнопки для навигации по датам</i>"
        
        await callback.message.edit_text(
            text,
            reply_markup=date_navigation_keyboard(new_date.isoformat()),
            parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {e}", show_alert=True)


@router.callback_query(F.data == "schedule_enter_date")
async def enter_date(callback: CallbackQuery, state: FSMContext):
    """Ввод даты вручную"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    
    text = (
        "✏️ <b>Введите дату</b>\n\n"
        "Формат: ДД.ММ.ГГГГ\n"
        "Например: 15.03.2025\n\n"
        "Или: ДД.ММ (текущий год)\n"
        "Например: 15.03"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(ScheduleStates.waiting_custom_date)
    await callback.answer()


@router.message(ScheduleStates.waiting_custom_date)
async def process_custom_date(message: Message, state: FSMContext):
    """Обработка введённой даты"""
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    
    import re
    
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
        await message.answer(
            "❌ Неверный формат даты.\n\n"
            "Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ\n"
            "Например: 15.03.2025 или 15.03\n\n"
            "Отправьте /schedule для отмены"
        )
        return
    
    await state.clear()
    
    schedule_text = await get_schedule_text(message.chat.id, parsed_date)
    schedule_text += "\n\n<i>Используйте кнопки для навигации по датам</i>"
    
    await message.answer(
        schedule_text,
        reply_markup=date_navigation_keyboard(parsed_date.isoformat()),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "next_prayer")
async def next_prayer(callback: CallbackQuery):
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
        minutes, _ = divmod(remainder, 60)
        
        if hours > 0:
            remaining = f"{hours} ч {minutes} мин"
        else:
            remaining = f"{minutes} мин"
        
        text = (
            f"⏰ <b>Следующий намаз</b>\n\n"
            f"{prayer_name}\n"
            f"🕐 Время: <b>{time}</b>\n"
            f"⏳ Осталось: <b>{remaining}</b>"
        )
    else:
        text = "❌ Не удалось определить следующий намаз"
    
    await callback.message.edit_text(
        text,
        reply_markup=schedule_keyboard(is_admin(callback.from_user.id)),
        parse_mode="HTML"
    )
    await callback.answer()