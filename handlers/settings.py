from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import (
    settings_keyboard, auto_schedule_keyboard,
    schedule_day_keyboard, prayer_names_style_keyboard,
    hijri_settings_keyboard, holidays_settings_keyboard,
    back_to_settings_keyboard
)
from database import get_chat_settings, save_chat_settings

router = Router()


class SettingsStates(StatesGroup):
    waiting_custom_time = State()


async def show_settings_message(message: Message):
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
        'standard': 'Стандартные',
        'crimean_cyrillic': 'Кириллица',
        'crimean_latin': 'Латиница'
    }
    
    day_text = "сегодня" if day == 'today' else "завтра"
    auto_text = auto_time if auto_time else "отключено"
    
    text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"⏰ Рассылка: <b>{auto_text}</b>\n"
        f"📆 В рассылке: <b>{day_text}</b>\n"
        f"🔤 Язык: <b>{style_names.get(style, 'Стандартные')}</b>\n"
        f"🗓 Дата по Хиджре: <b>{'вкл' if show_hijri else 'выкл'}</b>\n"
        f"🎉 Праздники: <b>{'вкл' if show_holidays else 'выкл'}</b>\n"
    )
    
    await message.answer(text, reply_markup=settings_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery):
    """Показать настройки"""
    settings = await get_chat_settings(callback.message.chat.id)
    
    auto_time = settings.get('daily_schedule_time') if settings else None
    day = settings.get('schedule_day', 'today') if settings else 'today'
    style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    show_hijri = settings.get('show_hijri', 1) if settings else 1
    show_holidays = settings.get('show_holidays', 1) if settings else 1
    
    style_names = {
        'standard': 'Стандартные',
        'crimean_cyrillic': 'Кириллица',
        'crimean_latin': 'Латиница'
    }
    
    day_text = "сегодня" if day == 'today' else "завтра"
    auto_text = auto_time if auto_time else "отключено"
    
    text = (
        "⚙️ <b>Настройки</b>\n\n"
        f"⏰ Рассылка: <b>{auto_text}</b>\n"
        f"📆 В рассылке: <b>{day_text}</b>\n"
        f"🔤 Язык: <b>{style_names.get(style, 'Стандартные')}</b>\n"
        f"🗓 Дата по Хиджре: <b>{'вкл' if show_hijri else 'выкл'}</b>\n"
        f"🎉 Праздники: <b>{'вкл' if show_holidays else 'выкл'}</b>\n"
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
        await callback.answer(f"✅ Рассылка установлена: {time_value}")
    
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


# === День расписания ===

@router.callback_query(F.data == "settings_day")
async def settings_day(callback: CallbackQuery):
    """Настройка дня расписания"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = settings.get('schedule_day', 'today') if settings else 'today'
    
    text = (
        "📆 <b>День расписания</b>\n\n"
        "Выберите какой день показывать в ежедневной рассылке:\n\n"
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