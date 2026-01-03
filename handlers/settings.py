from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import (
    settings_keyboard, auto_schedule_keyboard, offset_keyboard,
    prayer_offset_keyboard, prayer_offset_value_keyboard,
    schedule_day_keyboard, location_keyboard, prayer_names_style_keyboard,
    hijri_settings_keyboard, location_settings_keyboard, holidays_settings_keyboard,
    back_to_settings_keyboard
)
from database import get_chat_settings, save_chat_settings
from config import PRAYER_NAMES_STYLES

router = Router()


class SettingsStates(StatesGroup):
    waiting_custom_time = State()
    waiting_custom_offset = State()
    waiting_location_name = State()


async def show_settings_message(message: Message):
    """Показать настройки как сообщение"""
    settings = await get_chat_settings(message.chat.id)
    
    if not settings:
        await save_chat_settings(message.chat.id, message.chat.type)
        settings = await get_chat_settings(message.chat.id)
    
    auto_time = settings.get('daily_schedule_time') if settings else None
    offset = settings.get('time_offset', 0) if settings else 0
    day = settings.get('schedule_day', 'today') if settings else 'today'
    location = settings.get('location_name', 'Симферополь') if settings else 'Симферополь'
    style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    show_hijri = settings.get('show_hijri', 1) if settings else 1
    show_location = settings.get('show_location', 1) if settings else 1
    
    style_names = {
        'standard': 'Стандартные',
        'crimean_cyrillic': 'Кириллица',
        'crimean_latin': 'Латиница'
    }
    
    day_text = "сегодня" if day == 'today' else "завтра"
    auto_text = auto_time if auto_time else "отключено"
    
    text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"📍 Город: <b>{location}</b> {'(скрыт)' if not show_location else ''}\n"
        f"⏰ Рассылка: <b>{auto_text}</b>\n"
        f"⏱ Коррекция времени: <b>{offset:+d} мин</b>\n"
        f"📆 В рассылке: <b>{day_text}</b>\n"
        f"🔤 Язык: <b>{style_names.get(style, 'Стандартные')}</b>\n"
        f"🗓 Дата по Хиджре: <b>{'включена' if show_hijri else 'выключена'}</b>\n"
    )
    
    await message.answer(text, reply_markup=settings_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery):
    """Показать настройки"""
    settings = await get_chat_settings(callback.message.chat.id)
    
    auto_time = settings.get('daily_schedule_time') if settings else None
    offset = settings.get('time_offset', 0) if settings else 0
    day = settings.get('schedule_day', 'today') if settings else 'today'
    location = settings.get('location_name', 'Симферополь') if settings else 'Симферополь'
    style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    show_hijri = settings.get('show_hijri', 1) if settings else 1
    show_location = settings.get('show_location', 1) if settings else 1
    
    style_names = {
        'standard': 'Стандартные',
        'crimean_cyrillic': 'Кириллица',
        'crimean_latin': 'Латиница'
    }
    
    day_text = "сегодня" if day == 'today' else "завтра"
    auto_text = auto_time if auto_time else "отключено"
    
    text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"📍 Город: <b>{location}</b> {'(скрыт)' if not show_location else ''}\n"
        f"⏰ Рассылка: <b>{auto_text}</b>\n"
        f"⏱ Коррекция времени: <b>{offset:+d} мин</b>\n"
        f"📆 В рассылке: <b>{day_text}</b>\n"
        f"🔤 Язык: <b>{style_names.get(style, 'Стандартные')}</b>\n"
        f"🗓 Дата по Хиджре: <b>{'включена' if show_hijri else 'выключена'}</b>\n"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=settings_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# === Названия намазов ===

@router.callback_query(F.data == "settings_prayer_names")
async def settings_prayer_names(callback: CallbackQuery):
    """Настройка названий намазов"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    
    text = (
        "🔤 <b>Названия намазов</b>\n\n"
        "Выберите стиль отображения:\n\n"
        "• <b>Стандартные</b>: Фаджр, Зухр, Аср...\n"
        "• <b>Кириллица</b>: Имсак, Уйле, Экинди...\n"
        "• <b>Латиница</b>: İmsak, Üyle, Ekindi..."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=prayer_names_style_keyboard(current),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_prayer_style_"))
async def set_prayer_style(callback: CallbackQuery):
    """Установка стиля названий"""
    style = callback.data.replace("set_prayer_style_", "")
    await save_chat_settings(callback.message.chat.id, prayer_names_style=style)
    await callback.answer("✅ Стиль изменён")
    await settings_prayer_names(callback)


# === Настройки хиджри ===

@router.callback_query(F.data == "settings_hijri")
async def settings_hijri(callback: CallbackQuery):
    """Настройки хиджри"""
    settings = await get_chat_settings(callback.message.chat.id)
    show_hijri = bool(settings.get('show_hijri', 1)) if settings else True
    hijri_style = settings.get('hijri_style', 'cyrillic') if settings else 'cyrillic'
    
    text = (
        "📅 <b>Настройки хиджри</b>\n\n"
        f"Показывать дату: <b>{'да' if show_hijri else 'нет'}</b>\n"
        f"Стиль месяцев: <b>{'кириллица' if hijri_style == 'cyrillic' else 'латиница'}</b>\n\n"
        "Пример:\n"
        "• Кириллица: 15 Рамазан 1446 х.\n"
        "• Латиница: 15 Ramazan 1446 х."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=hijri_settings_keyboard(show_hijri, hijri_style),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_hijri")
async def toggle_hijri(callback: CallbackQuery):
    """Переключение отображения хиджри"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = bool(settings.get('show_hijri', 1)) if settings else True
    await save_chat_settings(callback.message.chat.id, show_hijri=0 if current else 1)
    await callback.answer("✅ Изменено")
    await settings_hijri(callback)


@router.callback_query(F.data.startswith("set_hijri_style_"))
async def set_hijri_style(callback: CallbackQuery):
    """Установка стиля хиджри"""
    style = callback.data.replace("set_hijri_style_", "")
    await save_chat_settings(callback.message.chat.id, hijri_style=style)
    await callback.answer("✅ Стиль изменён")
    await settings_hijri(callback)


# === Настройки локации ===

@router.callback_query(F.data == "settings_location")
async def settings_location(callback: CallbackQuery):
    """Настройки локации"""
    settings = await get_chat_settings(callback.message.chat.id)
    show_location = bool(settings.get('show_location', 1)) if settings else True
    location = settings.get('location_name', 'Симферополь') if settings else 'Симферополь'
    offset = settings.get('time_offset', 0) if settings else 0
    
    text = (
        "📍 <b>Настройки локации</b>\n\n"
        f"Название: <b>{location}</b>\n"
        f"Смещение: <b>{offset:+d} мин</b>\n"
        f"Показывать в расписании: <b>{'да' if show_location else 'нет'}</b>"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=location_settings_keyboard(show_location),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_location_display")
async def toggle_location_display(callback: CallbackQuery):
    """Переключение отображения локации"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = bool(settings.get('show_location', 1)) if settings else True
    await save_chat_settings(callback.message.chat.id, show_location=0 if current else 1)
    await callback.answer("✅ Изменено")
    await settings_location(callback)


@router.callback_query(F.data == "edit_location_name")
async def edit_location_name(callback: CallbackQuery, state: FSMContext):
    """Изменение названия локации"""
    await callback.message.edit_text(
        "✏️ Введите название локации:\n\n"
        "Например: Симферополь, Мой город, Дом",
        parse_mode="HTML"
    )
    await state.set_state(SettingsStates.waiting_location_name)
    await callback.answer()


@router.message(SettingsStates.waiting_location_name)
async def process_location_name(message: Message, state: FSMContext):
    """Обработка названия локации"""
    name = message.text.strip()[:50]  # Ограничение в 50 символов
    await save_chat_settings(message.chat.id, location_name=name)
    await state.clear()
    await message.answer(
        f"✅ Локация изменена: {name}\n\n"
        "Используйте /settings для возврата к настройкам."
    )


@router.callback_query(F.data == "manual_offset")
async def manual_offset(callback: CallbackQuery, state: FSMContext):
    """Ручной ввод смещения"""
    await callback.message.edit_text(
        "✏️ Введите поправку в минутах:\n\n"
        "Примеры: 5, -10, +15\n\n"
        "• <b>Положительное число</b> (+5) — намаз наступает позже\n"
        "• <b>Отрицательное число</b> (-5) — намаз наступает раньше\n\n",
        parse_mode="HTML"
    )
    await state.set_state(SettingsStates.waiting_custom_offset)
    await callback.answer()


@router.message(SettingsStates.waiting_custom_offset)
async def process_custom_offset(message: Message, state: FSMContext):
    """Обработка пользовательского смещения"""
    try:
        offset = int(message.text.replace("+", ""))
        if -120 <= offset <= 120:
            await save_chat_settings(message.chat.id, time_offset=offset)
            await state.clear()
            await message.answer(
                f"✅ Смещение установлено: {offset:+d} мин\n\n"
                "Используйте /settings для возврата к настройкам."
            )
        else:
            await message.answer("❌ Смещение должно быть от -120 до +120 минут")
    except ValueError:
        await message.answer("❌ Введите число. Например: 5, -10, +15")


# === Настройки праздников ===

@router.callback_query(F.data == "settings_holidays")
async def settings_holidays(callback: CallbackQuery):
    """Настройки праздников"""
    settings = await get_chat_settings(callback.message.chat.id)
    show_holidays = bool(settings.get('show_holidays', 1)) if settings else True
    
    text = (
        "🎉 <b>Настройки праздников</b>\n\n"
        f"Показывать праздники: <b>{'да' if show_holidays else 'нет'}</b>\n\n"
        "Когда включено:\n"
        "• Праздники отображаются в расписании\n"
        "• Напоминание за день до священной ночи\n"
        "• Обратный отсчёт до Рамазана"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=holidays_settings_keyboard(show_holidays),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_holidays")
async def toggle_holidays(callback: CallbackQuery):
    """Переключение отображения праздников"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = bool(settings.get('show_holidays', 1)) if settings else True
    await save_chat_settings(callback.message.chat.id, show_holidays=0 if current else 1)
    await callback.answer("✅ Изменено")
    await settings_holidays(callback)


@router.callback_query(F.data == "holidays_list")
async def holidays_list(callback: CallbackQuery):
    """Переход к списку праздников"""
    from handlers.start import show_holidays
    await show_holidays(callback)


# === Авто-расписание ===

@router.callback_query(F.data == "settings_auto")
async def settings_auto(callback: CallbackQuery):
    """Настройка авто-расписания"""
    settings = await get_chat_settings(callback.message.chat.id)
    current_time = settings.get('daily_schedule_time') if settings else None
    
    text = (
        "⏰ <b>Ежедневная рассылка</b>\n\n"
        "Во сколько присылать расписание на день?\n\n"
        f"Текущее время: <b>{current_time or 'не установлено'}</b>"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=auto_schedule_keyboard(current_time),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_auto_time_"))
async def set_auto_time(callback: CallbackQuery, state: FSMContext):
    """Установка времени авто-расписания"""
    time_value = callback.data.replace("set_auto_time_", "")
    
    if time_value == "custom":
        await callback.message.edit_text(
            "✏️ Введите время в формате ЧЧ:ММ\n"
            "Например: 07:30",
            parse_mode="HTML"
        )
        await state.set_state(SettingsStates.waiting_custom_time)
        await callback.answer()
        return
    
    if time_value == "off":
        await save_chat_settings(callback.message.chat.id, daily_schedule_time=None)
        await callback.answer("✅ Ежедневная рассылка отключена")
    else:
        await save_chat_settings(callback.message.chat.id, daily_schedule_time=time_value)
        await callback.answer(f"✅ Ежедневная рассылка установлена: {time_value}")
    
    await settings_auto(callback)


@router.message(SettingsStates.waiting_custom_time)
async def process_custom_time(message: Message, state: FSMContext):
    """Обработка пользовательского времени"""
    import re
    
    time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$')
    
    if time_pattern.match(message.text):
        await save_chat_settings(message.chat.id, daily_schedule_time=message.text)
        await state.clear()
        await message.answer(
            f"✅ Время установлено: {message.text}\n\n"
            "Используйте /settings для возврата к настройкам."
        )
    else:
        await message.answer(
            "❌ Неверный формат. Введите время в формате ЧЧ:ММ\n"
            "Например: 07:30"
        )


# === Смещение времени ===

@router.callback_query(F.data == "settings_offset")
async def settings_offset(callback: CallbackQuery):
    """Настройка смещения времени"""
    settings = await get_chat_settings(callback.message.chat.id)
    current_offset = settings.get('time_offset', 0) if settings else 0
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES['standard'])
    
    text = (
        "⏱ <b>Смещение времени</b>\n\n"
        f"Общее смещение: <b>{current_offset:+d} мин</b>\n\n"
    )
    
    if prayer_offsets:
        text += "Индивидуальные смещения:\n"
        for prayer, offset in prayer_offsets.items():
            if offset != 0:
                text += f"• {prayer_names[prayer]}: {offset:+d} мин\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=offset_keyboard(current_offset),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("offset_") & ~F.data.startswith("offset_per_prayer"))
async def change_offset(callback: CallbackQuery):
    """Изменение смещения"""
    action = callback.data.replace("offset_", "")
    
    if action == "reset":
        await save_chat_settings(callback.message.chat.id, time_offset=0)
        await callback.answer("✅ Смещение сброшено")
    else:
        settings = await get_chat_settings(callback.message.chat.id)
        current = settings.get('time_offset', 0) if settings else 0
        change = int(action)
        new_offset = current + change
        await save_chat_settings(callback.message.chat.id, time_offset=new_offset)
        await callback.answer(f"Смещение: {new_offset:+d} мин")
    
    await settings_offset(callback)


@router.callback_query(F.data == "offset_per_prayer")
async def offset_per_prayer(callback: CallbackQuery):
    """Переход к индивидуальным смещениям"""
    await show_prayer_offsets(callback)


async def show_prayer_offsets(callback: CallbackQuery):
    """Показать выбор намаза для смещения"""
    settings = await get_chat_settings(callback.message.chat.id)
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES['standard'])
    
    text = "⏱ <b>Смещение по намазам</b>\n\n"
    text += "Выберите намаз для настройки:\n\n"
    
    for prayer in ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]:
        offset = prayer_offsets.get(prayer, 0)
        text += f"• {prayer_names[prayer]}: <b>{offset:+d} мин</b>\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=prayer_offset_keyboard(prayer_names_style),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prayer_offset_"))
async def select_prayer_offset(callback: CallbackQuery):
    """Выбор намаза для смещения"""
    prayer_key = callback.data.replace("prayer_offset_", "")
    
    settings = await get_chat_settings(callback.message.chat.id)
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    current_offset = prayer_offsets.get(prayer_key, 0)
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES['standard'])
    
    text = (
        f"⏱ <b>Смещение для {prayer_names[prayer_key]}</b>\n\n"
        f"Текущее смещение: <b>{current_offset:+d} мин</b>\n\n"
        "Выберите изменение:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=prayer_offset_value_keyboard(prayer_key, current_offset),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_prayer_offset_"))
async def set_prayer_offset(callback: CallbackQuery):
    """Установка смещения для намаза"""
    parts = callback.data.replace("set_prayer_offset_", "").rsplit("_", 1)
    prayer_key = parts[0]
    change = int(parts[1])
    
    settings = await get_chat_settings(callback.message.chat.id)
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    
    if change == 0:
        prayer_offsets.pop(prayer_key, None)
    else:
        current = prayer_offsets.get(prayer_key, 0)
        prayer_offsets[prayer_key] = current + change
    
    await save_chat_settings(callback.message.chat.id, prayer_offsets=prayer_offsets)
    await callback.answer(f"✅ Смещение обновлено")
    
    await select_prayer_offset(callback)


# === День расписания ===

@router.callback_query(F.data == "settings_day")
async def settings_day(callback: CallbackQuery):
    """Настройка дня расписания"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = settings.get('schedule_day', 'today') if settings else 'today'
    
    text = (
        "📆 <b>День расписания</b>\n\n"
        "Выберите какой день показывать при авто-отправке:\n\n"
        f"Текущий выбор: <b>{'Сегодня' if current == 'today' else 'Завтра'}</b>"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=schedule_day_keyboard(current),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_day_"))
async def set_day(callback: CallbackQuery):
    """Установка дня"""
    day = callback.data.replace("set_day_", "")
    await save_chat_settings(callback.message.chat.id, schedule_day=day)
    await callback.answer(f"✅ Выбран: {'сегодня' if day == 'today' else 'завтра'}")
    await settings_day(callback)


# === Локация (выбор города) ===

@router.callback_query(F.data == "location")
async def show_location(callback: CallbackQuery):
    """Показать выбор локации"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = settings.get('location_name', 'Симферополь') if settings else 'Симферополь'
    offset = settings.get('time_offset', 0) if settings else 0
    
    text = (
        "📍 <b>Локация</b>\n\n"
        f"Текущая: <b>{current}</b>\n"
        f"Смещение: <b>{offset:+d} мин</b>\n\n"
        "Выберите город или настройте смещение вручную:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=location_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_location_"))
async def set_location(callback: CallbackQuery):
    """Установка локации"""
    parts = callback.data.replace("set_location_", "").rsplit("_", 1)
    name = parts[0]
    offset = int(parts[1])
    
    await save_chat_settings(
        callback.message.chat.id,
        location_name=name,
        time_offset=offset
    )
    
    await callback.answer(f"✅ Локация: {name} ({offset:+d} мин)")
    await show_location(callback)