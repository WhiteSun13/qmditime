from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import (
    location_keyboard, custom_location_menu_keyboard, 
    offset_menu_keyboard, general_offset_keyboard,
    prayer_offsets_keyboard, prayer_offset_values_keyboard,
    back_to_main_keyboard
)
from database import get_chat_settings, save_chat_settings
from config import LOCATIONS, PRAYER_NAMES_STYLES

router = Router()


class LocationStates(StatesGroup):
    waiting_city_name = State()
    waiting_general_offset = State()
    waiting_prayer_offset = State()


@router.callback_query(F.data == "location")
async def show_location(callback: CallbackQuery, state: FSMContext):
    """Показать выбор локации"""
    await state.clear()
    
    settings = await get_chat_settings(callback.message.chat.id)
    current = settings.get('location_name', 'Акъмесджит (Симферополь)') if settings else 'Акъмесджит (Симферополь)'
    offset = settings.get('time_offset', 0) if settings else 0
    show_loc = bool(settings.get('show_location', 1)) if settings else True
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    
    text = (
        "📍 <b>Выбор локации</b>\n\n"
        f"Текущий: <b>{current}</b>\n"
        f"Общее смещение: <b>{offset:+d} мин</b>\n"
    )
    
    if prayer_offsets and any(v != 0 for v in prayer_offsets.values()):
        text += "Индивидуальные смещения: <b>настроены</b>\n"
    
    text += "\nВыберите ваш город или укажите другой:"
    
    await callback.message.edit_text(
        text,
        reply_markup=location_keyboard(current, show_loc),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_location_display")
async def toggle_location_display(callback: CallbackQuery, state: FSMContext):
    """Переключение отображения названия города"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = bool(settings.get('show_location', 1)) if settings else True
    await save_chat_settings(callback.message.chat.id, show_location=0 if current else 1)
    await callback.answer("✅ Изменено")
    await show_location(callback, state)


@router.callback_query(F.data.startswith("set_loc_"))
async def set_location_from_list(callback: CallbackQuery, state: FSMContext):
    """Установка города из списка"""
    try:
        idx = int(callback.data.replace("set_loc_", ""))
        if 0 <= idx < len(LOCATIONS):
            name, offset = LOCATIONS[idx]
            await save_chat_settings(
                callback.message.chat.id,
                location_name=name,
                time_offset=offset,
                prayer_offsets={}  # Сброс индивидуальных смещений при выборе города
            )
            await callback.answer(f"✅ {name} ({offset:+d} мин)")
            await show_location(callback, state)
        else:
            await callback.answer("❌ Город не найден", show_alert=True)
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка", show_alert=True)


# === Меню "Другая локация" ===

@router.callback_query(F.data == "custom_location")
async def custom_location_menu(callback: CallbackQuery, state: FSMContext):
    """Меню другой локации"""
    await state.clear()
    
    settings = await get_chat_settings(callback.message.chat.id)
    current_name = settings.get('location_name', 'Симферополь') if settings else 'Симферополь'
    general_offset = settings.get('time_offset', 0) if settings else 0
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    
    text = (
        "🏙 <b>Другая локация</b>\n\n"
        f"📍 Название: <b>{current_name}</b>\n"
        f"⏱ Общее смещение: <b>{general_offset:+d} мин</b>\n"
    )
    
    if prayer_offsets and any(v != 0 for v in prayer_offsets.values()):
        text += "🕌 Индивидуальные смещения: <b>настроены</b>\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=custom_location_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


# === Ввод названия ===

@router.callback_query(F.data == "enter_city_name")
async def enter_city_name(callback: CallbackQuery, state: FSMContext):
    """Начать ввод названия города"""
    text = (
        "📝 <b>Название локации</b>\n\n"
        "Введите название вашей локации:\n\n"
        "<i>Например: Демерджи, Новофёдоровка, Мой дом</i>"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(LocationStates.waiting_city_name)
    await callback.answer()


@router.message(LocationStates.waiting_city_name)
async def process_city_name(message: Message, state: FSMContext):
    """Обработка названия города"""
    name = message.text.strip()[:50]
    
    if not name:
        await message.answer("❌ Название не может быть пустым. Попробуйте ещё раз:")
        return
    
    await save_chat_settings(message.chat.id, location_name=name)
    await state.clear()
    
    settings = await get_chat_settings(message.chat.id)
    general_offset = settings.get('time_offset', 0) if settings else 0
    
    await message.answer(
        f"✅ Название установлено: <b>{name}</b>\n\n"
        f"Текущее смещение: <b>{general_offset:+d} мин</b>\n\n"
        "Используйте /start для возврата в меню.",
        parse_mode="HTML"
    )


# === Меню смещения ===

@router.callback_query(F.data == "offset_menu")
async def offset_menu(callback: CallbackQuery, state: FSMContext):
    """Меню смещения времени"""
    await state.clear()
    
    settings = await get_chat_settings(callback.message.chat.id)
    general_offset = settings.get('time_offset', 0) if settings else 0
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    has_prayer_offsets = bool(prayer_offsets and any(v != 0 for v in prayer_offsets.values()))
    
    text = (
        "⏱ <b>Смещение времени</b>\n\n"
        f"Общее смещение: <b>{general_offset:+d} мин</b>\n"
    )
    
    if has_prayer_offsets:
        text += "Индивидуальные смещения: <b>настроены</b>\n"
    
    text += (
        "\n• <b>Общее смещение</b> — применяется ко всем намазам\n"
        "• <b>По намазам</b> — дополнительная настройка для каждого намаза"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=offset_menu_keyboard(general_offset, has_prayer_offsets),
        parse_mode="HTML"
    )
    await callback.answer()


# === Общее смещение ===

@router.callback_query(F.data == "offset_general")
async def offset_general(callback: CallbackQuery, state: FSMContext):
    """Настройка общего смещения"""
    settings = await get_chat_settings(callback.message.chat.id)
    general_offset = settings.get('time_offset', 0) if settings else 0
    
    text = (
        f"⏱ <b>Общее смещение</b>\n\n"
        f"Текущее: <b>{general_offset:+d} мин</b>\n\n"
        "• <b>Положительное</b> (+5) — намаз позже\n"
        "• <b>Отрицательное</b> (-5) — намаз раньше\n\n"
        "Выберите смещение:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=general_offset_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_general_offset_"))
async def set_general_offset(callback: CallbackQuery, state: FSMContext):
    """Установка общего смещения"""
    offset = int(callback.data.replace("set_general_offset_", ""))
    await save_chat_settings(callback.message.chat.id, time_offset=offset)
    await callback.answer(f"✅ Общее смещение: {offset:+d} мин")
    await offset_menu(callback, state)


@router.callback_query(F.data == "general_offset_manual")
async def general_offset_manual(callback: CallbackQuery, state: FSMContext):
    """Ручной ввод общего смещения"""
    await callback.message.edit_text(
        "✏️ <b>Ввод смещения</b>\n\n"
        "Введите смещение в минутах:\n\n"
        "Примеры: 5, -10, +15",
        parse_mode="HTML"
    )
    await state.set_state(LocationStates.waiting_general_offset)
    await callback.answer()


@router.message(LocationStates.waiting_general_offset)
async def process_general_offset(message: Message, state: FSMContext):
    """Обработка ввода общего смещения"""
    try:
        offset = int(message.text.strip().replace("+", ""))
        
        if not (-120 <= offset <= 120):
            await message.answer(
                "❌ Смещение должно быть от -120 до +120 минут\n"
                "Попробуйте ещё раз:"
            )
            return
        
        await save_chat_settings(message.chat.id, time_offset=offset)
        await state.clear()
        
        await message.answer(
            f"✅ Общее смещение установлено: {offset:+d} мин\n\n"
            "Используйте /start для возврата в меню."
        )
        
    except ValueError:
        await message.answer(
            "❌ Введите число.\n"
            "Например: 5, -10, +15\n\n"
            "Попробуйте ещё раз:"
        )


# === Смещение по намазам ===

@router.callback_query(F.data == "offset_by_prayer")
async def offset_by_prayer(callback: CallbackQuery, state: FSMContext):
    """Настройка смещения по намазам"""
    settings = await get_chat_settings(callback.message.chat.id)
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    general_offset = settings.get('time_offset', 0) if settings else 0
    
    text = (
        "🕌 <b>Смещение по намазам</b>\n\n"
        f"Общее смещение: <b>{general_offset:+d} мин</b>\n\n"
        "Индивидуальное смещение <b>добавляется</b> к общему.\n"
        "Например: общее +5 и Фаджр +2 = итого +7 мин для Фаджра.\n\n"
        "Выберите намаз:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=prayer_offsets_keyboard(prayer_offsets, prayer_names_style),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prayer_offset_") & ~F.data.startswith("prayer_offset_reset") & ~F.data.startswith("prayer_offset_manual"))
async def select_prayer_offset(callback: CallbackQuery, state: FSMContext):
    """Выбор намаза для смещения"""
    prayer_key = callback.data.replace("prayer_offset_", "")
    
    settings = await get_chat_settings(callback.message.chat.id)
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    current_offset = prayer_offsets.get(prayer_key, 0)
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES['standard'])
    
    await state.update_data(current_prayer_key=prayer_key)
    
    text = (
        f"⏱ <b>Смещение для {prayer_names[prayer_key]}</b>\n\n"
        f"Текущее: <b>{current_offset:+d} мин</b>\n\n"
        "Выберите смещение:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=prayer_offset_values_keyboard(prayer_key),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_prayer_offset_"))
async def set_prayer_offset(callback: CallbackQuery, state: FSMContext):
    """Установка смещения для намаза"""
    parts = callback.data.replace("set_prayer_offset_", "").rsplit("_", 1)
    prayer_key = parts[0]
    offset = int(parts[1])
    
    settings = await get_chat_settings(callback.message.chat.id)
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    
    if offset == 0:
        prayer_offsets.pop(prayer_key, None)
    else:
        prayer_offsets[prayer_key] = offset
    
    await save_chat_settings(callback.message.chat.id, prayer_offsets=prayer_offsets)
    await callback.answer(f"✅ Смещение: {offset:+d} мин")
    await offset_by_prayer(callback, state)


@router.callback_query(F.data.startswith("prayer_offset_manual_"))
async def prayer_offset_manual(callback: CallbackQuery, state: FSMContext):
    """Ручной ввод смещения для намаза"""
    prayer_key = callback.data.replace("prayer_offset_manual_", "")
    await state.update_data(current_prayer_key=prayer_key)
    
    settings = await get_chat_settings(callback.message.chat.id)
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES['standard'])
    
    await callback.message.edit_text(
        f"✏️ <b>Смещение для {prayer_names[prayer_key]}</b>\n\n"
        "Введите смещение в минутах:\n\n"
        "Примеры: 5, -10, +15",
        parse_mode="HTML"
    )
    await state.set_state(LocationStates.waiting_prayer_offset)
    await callback.answer()


@router.message(LocationStates.waiting_prayer_offset)
async def process_prayer_offset(message: Message, state: FSMContext):
    """Обработка ввода смещения для намаза"""
    try:
        offset = int(message.text.strip().replace("+", ""))
        
        if not (-120 <= offset <= 120):
            await message.answer(
                "❌ Смещение должно быть от -120 до +120 минут\n"
                "Попробуйте ещё раз:"
            )
            return
        
        data = await state.get_data()
        prayer_key = data.get('current_prayer_key')
        
        if not prayer_key:
            await state.clear()
            await message.answer("❌ Ошибка. Попробуйте снова через /start")
            return
        
        settings = await get_chat_settings(message.chat.id)
        prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
        
        if offset == 0:
            prayer_offsets.pop(prayer_key, None)
        else:
            prayer_offsets[prayer_key] = offset
        
        await save_chat_settings(message.chat.id, prayer_offsets=prayer_offsets)
        await state.clear()
        
        await message.answer(
            f"✅ Смещение установлено: {offset:+d} мин\n\n"
            "Используйте /start для возврата в меню."
        )
        
    except ValueError:
        await message.answer(
            "❌ Введите число.\n"
            "Например: 5, -10, +15\n\n"
            "Попробуйте ещё раз:"
        )


@router.callback_query(F.data == "prayer_offset_reset_all")
async def reset_all_prayer_offsets(callback: CallbackQuery, state: FSMContext):
    """Сброс всех индивидуальных смещений"""
    await save_chat_settings(callback.message.chat.id, prayer_offsets={})
    await callback.answer("✅ Все индивидуальные смещения сброшены")
    await offset_by_prayer(callback, state)