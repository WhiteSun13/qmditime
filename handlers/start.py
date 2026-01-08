from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from keyboards.inline import main_menu_keyboard, schedule_keyboard
from database import save_chat_settings, get_chat_settings
from prayer_times import prayer_manager
from datetime import datetime, timedelta, date
import pytz
from config import TIMEZONE, PRAYER_NAMES_STYLES, HOLIDAYS, ADMIN_ID

def is_admin(user_id: int) -> bool:
    """Проверка является ли пользователь админом"""
    return user_id in ADMIN_ID


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработка команды /start"""
    chat_type = message.chat.type
    
    await save_chat_settings(
        chat_id=message.chat.id,
        chat_type=chat_type
    )
    
    text = (
        "🕌 <b>Ассаляму алейкум!</b>\n\n"
        "Я бот для получения расписания намаза в Крыму.\n\n"
        "<b>Мои возможности:</b>\n"
        "📅 Расписание намаза\n"
        "🗓 Дата по исламскому календарю (хиджри)\n"
        "🎉 Информация о праздниках и священных ночах\n"
        "🔔 Напоминания перед каждым намазом\n"
        "⏱ Корректировка времени\n"
        "Выберите нужный раздел:"
)
    
    await message.answer(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Команда /settings"""
    from handlers.settings import show_settings_message
    await show_settings_message(message)


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    text = (
        "🕌 <b>Главное меню</b>\n\n"
        "Выберите действие:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Показать помощь"""
    text = (
        "❓ <b>Справка по боту</b>\n\n"
        "<b>Быстрые команды:</b>\n"
        "/start — главное меню\n"
        "/schedule — расписание на сегодня\n"
        "/tomorrow — расписание на завтра\n"
        "/next — ближайший намаз\n"
        "/settings — настройки бота\n"
        "/holidays — список праздников\n\n"
        "<b>Описание настроек:</b>\n"
        "• <b>Ежедневная рассылка</b> — получайте расписание каждый день в выбранное время\n"
        "• <b>Смещение времени</b> — подстройка времени под вашу локацию\n"
        "• <b>Названия намазов</b> — стандартные, на кириллице или латинице\n"
        "• <b>Хиджри</b> — отображение даты по исламскому календарю\n"
        "• <b>Праздники</b> — показ праздников в расписании\n"
        "• <b>Напоминания</b> — уведомления за N минут до намаза\n\n"
        "<b>Использование в группах:</b>\n"
        "Добавьте бота в группу и используйте /settings для настройки"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "holidays")
async def show_holidays(callback: CallbackQuery):
    """Показать список праздников"""
    tz = pytz.timezone(TIMEZONE)
    current_year = datetime.now(tz).year
    
    year_holidays = HOLIDAYS.get(current_year, {})
    
    if not year_holidays:
        text = f"❌ Праздники на {current_year} год не найдены"
    else:
        text = f"🎉 <b>Праздники и особые дни {current_year}</b>\n\n"
        
        months_ru = [
            "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        
        # Группируем по месяцам
        by_month = {}
        for (month, day), info in sorted(year_holidays.items()):
            if month not in by_month:
                by_month[month] = []
            by_month[month].append((day, info))
        
        for month in sorted(by_month.keys()):
            text += f"\n<b>{months_ru[month]}</b>\n"
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
                            text += f"  {prev_date.day} {months_ru[prev_date.month]}-{day}: {emoji} {info['name']}\n"
                    except:
                        text += f"  {day}: {emoji} {info['name']}\n"
                else:
                    text += f"  {day}: {emoji} {info['name']}\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.message(Command("holidays"))
async def cmd_holidays(message: Message):
    """Команда /holidays"""
    tz = pytz.timezone(TIMEZONE)
    current_year = datetime.now(tz).year
    
    year_holidays = HOLIDAYS.get(current_year, {})
    
    if not year_holidays:
        text = f"❌ Праздники на {current_year} год не найдены"
    else:
        text = f"🎉 <b>Праздники и особые дни {current_year}</b>\n\n"
        
        months_ru = [
            "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        
        by_month = {}
        for (month, day), info in sorted(year_holidays.items()):
            if month not in by_month:
                by_month[month] = []
            by_month[month].append((day, info))
        
        for month in sorted(by_month.keys()):
            text += f"\n<b>{months_ru[month]}</b>\n"
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
                            text += f"  {prev_date.day} {months_ru[prev_date.month]}-{day}: {emoji} {info['name']}\n"
                    except:
                        text += f"  {day}: {emoji} {info['name']}\n"
                else:
                    text += f"  {day}: {emoji} {info['name']}\n"
    
    await message.answer(text, parse_mode="HTML")


# Обновить команду /schedule:
@router.message(Command("schedule"))
async def cmd_schedule(message: Message):
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
        hijri_style=settings.get('hijri_style', 'cyrillic'),
        show_holidays=bool(settings.get('show_holidays', 1))
    )
    
    await message.answer(
        text,
        reply_markup=schedule_keyboard(is_admin(message.from_user.id)),
        parse_mode="HTML"
    )


@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message):
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
        hijri_style=settings.get('hijri_style', 'cyrillic'),
        show_holidays=bool(settings.get('show_holidays', 1))
    )
    
    await message.answer(
        text,
        reply_markup=schedule_keyboard(is_admin(message.from_user.id)),
        parse_mode="HTML"
    )


@router.message(Command("next"))
async def cmd_next(message: Message):
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
    
    await message.answer(
        text,
        reply_markup=schedule_keyboard(is_admin(message.from_user.id)),
        parse_mode="HTML"
    )


@router.message(Command("reload"))
async def cmd_reload(message: Message):
    """Перезагрузка данных CSV (только для админов)"""
    if message.from_user.id not in ADMIN_ID:
        await message.answer("⛔ Нет доступа")
        return
    
    try:
        prayer_manager.load_data()
        rows = len(prayer_manager.df)
        await message.answer(f"✅ Данные перезагружены\n📊 Загружено {rows} дней")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@router.message(Command("export"))
async def cmd_export(message: Message):
    """Экспорт базы данных (только для админов)"""
    if message.from_user.id not in ADMIN_ID:
        await message.answer("⛔ Нет доступа")
        return
    
    from config import DATABASE_PATH
    import os
    
    if not os.path.exists(DATABASE_PATH):
        await message.answer("❌ База данных не найдена")
        return
    
    try:
        file = FSInputFile(DATABASE_PATH, filename="prayer_bot_backup.db")
        await message.answer_document(
            file,
            caption=f"📦 <b>Экспорт базы данных</b>\n\n"
                    f"📅 Дата: {datetime.now(pytz.timezone(TIMEZONE)).strftime('%d.%m.%Y %H:%M')}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка экспорта: {e}")