from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import location_keyboard, custom_location_offset_keyboard, back_to_main_keyboard
from database import get_chat_settings, save_chat_settings
from config import LOCATIONS

router = Router()


class LocationStates(StatesGroup):
    waiting_city_name = State()
    waiting_custom_offset = State()


@router.callback_query(F.data == "location")
async def show_location(callback: CallbackQuery, state: FSMContext):
    """Показать выбор локации"""
    # Очищаем состояние если было
    await state.clear()
    
    settings = await get_chat_settings(callback.message.chat.id)
    current = settings.get('location_name', 'Акъмесджит (Симферополь)') if settings else 'Акъмесджит (Симферополь)'
    offset = settings.get('time_offset', 0) if settings else 0
    show_loc = bool(settings.get('show_location', 1)) if settings else True
    
    text = (
        "📍 <b>Выбор локации</b>\n\n"
        f"Текущий: <b>{current}</b>\n"
        f"Смещение: <b>{offset:+d} мин</b>\n\n"
        "Выберите ваш город или укажите другой:"
    )
    
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
                time_offset=offset
            )
            await callback.answer(f"✅ {name} ({offset:+d} мин)")
            await show_location(callback, state)
        else:
            await callback.answer("❌ Город не найден", show_alert=True)
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data == "custom_location")
async def custom_location_start(callback: CallbackQuery, state: FSMContext):
    """Начать ввод другого города"""
    text = (
        "🏙 <b>Другой город</b>\n\n"
        "Введите название вашей локации (населённого пункта):\n\n"
        "<i>Например: Демерджи, Новофёдоровка, Мой дом</i>"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(LocationStates.waiting_city_name)
    await callback.answer()


@router.message(LocationStates.waiting_city_name)
async def process_city_name(message: Message, state: FSMContext):
    """Обработка названия города"""
    name = message.text.strip()[:50]  # Ограничение в 50 символов
    
    if not name:
        await message.answer("❌ Название не может быть пустым. Попробуйте ещё раз:")
        return
    
    await state.update_data(city_name=name)
    
    text = (
        f"🏙 Город: <b>{name}</b>\n\n"
        "Теперь укажите смещение времени в минутах:\n\n"
        "• <b>Положительное</b> (+5) — намаз позже чем в Симферополе\n"
        "• <b>Отрицательное</b> (-5) — намаз раньше чем в Симферополе\n"
        "• <b>0</b> — время как в Симферополе"
    )
    
    await message.answer(
        text,
        reply_markup=custom_location_offset_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("custom_offset_"))
async def process_offset_button(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора смещения кнопкой"""
    offset_str = callback.data.replace("custom_offset_", "")
    
    if offset_str == "manual":
        await callback.message.edit_text(
            "✏️ <b>Ввод смещения</b>\n\n"
            "Введите смещение в минутах:\n\n"
            "Примеры: 5, -10, +15",
            parse_mode="HTML"
        )
        await state.set_state(LocationStates.waiting_custom_offset)
        await callback.answer()
        return
    
    try:
        offset = int(offset_str)
    except ValueError:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    data = await state.get_data()
    city_name = data.get('city_name')
    
    if not city_name:
        await callback.answer("❌ Сначала введите название локации", show_alert=True)
        await state.clear()
        return
    
    await save_chat_settings(
        callback.message.chat.id,
        location_name=city_name,
        time_offset=offset
    )
    
    await state.clear()
    await callback.answer(f"✅ {city_name} ({offset:+d} мин)")
    
    # Показываем обновлённое меню локации
    settings = await get_chat_settings(callback.message.chat.id)
    show_loc = bool(settings.get('show_location', 1)) if settings else True
    
    text = (
        "📍 <b>Выбор локации</b>\n\n"
        f"Текущий: <b>{city_name}</b>\n"
        f"Смещение: <b>{offset:+d} мин</b>\n\n"
        "Выберите ваш город или укажите другой:"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=location_keyboard(city_name, show_loc),
        parse_mode="HTML"
    )


@router.message(LocationStates.waiting_custom_offset)
async def process_offset_text(message: Message, state: FSMContext):
    """Обработка ввода смещения текстом"""
    try:
        offset = int(message.text.strip().replace("+", ""))
        
        if not (-120 <= offset <= 120):
            await message.answer(
                "❌ Смещение должно быть от -120 до +120 минут\n"
                "Попробуйте ещё раз:"
            )
            return
        
        data = await state.get_data()
        city_name = data.get('city_name', 'Мой город')
        
        await save_chat_settings(
            message.chat.id,
            location_name=city_name,
            time_offset=offset
        )
        
        await state.clear()
        
        settings = await get_chat_settings(message.chat.id)
        show_loc = bool(settings.get('show_location', 1)) if settings else True
        
        text = (
            f"✅ Локация установлена!\n\n"
            f"📍 <b>{city_name}</b>\n"
            f"⏱ Смещение: <b>{offset:+d} мин</b>"
        )
        
        await message.answer(
            text,
            reply_markup=location_keyboard(city_name, show_loc),
            parse_mode="HTML"
        )
        
    except ValueError:
        await message.answer(
            "❌ Введите число.\n"
            "Например: 5, -10, +15\n\n"
            "Попробуйте ещё раз:"
        )