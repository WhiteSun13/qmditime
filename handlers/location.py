from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline import (
    location_keyboard, custom_location_menu_keyboard, 
    offset_menu_keyboard, general_offset_keyboard,
    prayer_offsets_keyboard, prayer_offset_values_keyboard
)
from database import get_chat_settings, save_chat_settings
from config import LOCATIONS, PRAYER_NAMES_STYLES
from locales import get_text

router = Router()


class LocationStates(StatesGroup):
    waiting_city_name = State()
    waiting_general_offset = State()
    waiting_prayer_offset = State()


# === Вспомогательные функции для показа меню ===

async def _show_custom_location_menu(chat_id: int, message: Message, lang: str):
    """Показать меню другой локации"""
    _ = lambda key: get_text(lang, key)
    settings = await get_chat_settings(chat_id)
    current_name = settings.get('location_name', 'Симферополь') if settings else 'Симферополь'
    general_offset = settings.get('time_offset', 0) if settings else 0
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    
    text = (
        f"{_('custom_location_title')}\n\n"
        f"{_('custom_location_name')} <b>{current_name}</b>\n"
        f"{_('custom_location_offset')} <b>{general_offset:+d} {_('minutes')}</b>\n"
    )
    
    if prayer_offsets and any(v != 0 for v in prayer_offsets.values()):
        text += f"🕌 {_('location_individual')} <b>{_('location_configured')}</b>\n"
    
    await message.edit_text(
        text,
        reply_markup=custom_location_menu_keyboard(lang),
        parse_mode="HTML"
    )


async def _show_offset_menu(chat_id: int, message: Message, lang: str):
    """Показать меню смещения"""
    _ = lambda key: get_text(lang, key)
    settings = await get_chat_settings(chat_id)
    general_offset = settings.get('time_offset', 0) if settings else 0
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    has_prayer_offsets = bool(prayer_offsets and any(v != 0 for v in prayer_offsets.values()))
    
    text = (
        f"{_('offset_title')}\n\n"
        f"{_('offset_general')} <b>{general_offset:+d} {_('minutes')}</b>\n"
    )
    
    if has_prayer_offsets:
        text += f"{_('offset_individual_set')} <b>{_('location_configured')}</b>\n"
    
    text += (
        f"\n{_('offset_desc_general')}\n"
        f"{_('offset_desc_prayer')}"
    )
    
    await message.edit_text(
        text,
        reply_markup=offset_menu_keyboard(general_offset, has_prayer_offsets, lang),
        parse_mode="HTML"
    )


async def _show_prayer_offsets_menu(chat_id: int, message: Message, lang: str):
    """Показать меню смещения по намазам"""
    _ = lambda key: get_text(lang, key)
    settings = await get_chat_settings(chat_id)
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    general_offset = settings.get('time_offset', 0) if settings else 0
    
    text = (
        f"{_('prayer_offset_title')}\n\n"
        f"{_('offset_general')} <b>{general_offset:+d} {_('minutes')}</b>\n\n"
        f"{_('prayer_offset_desc')}\n\n"
        f"{_('select_prayer')}"
    )
    
    await message.edit_text(
        text,
        reply_markup=prayer_offsets_keyboard(prayer_offsets, prayer_names_style, lang),
        parse_mode="HTML"
    )


# === Основные обработчики ===

@router.callback_query(F.data == "location")
async def show_location(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Показать выбор локации"""
    await state.clear()
    
    settings = await get_chat_settings(callback.message.chat.id)
    current = settings.get('location_name', 'Акъмесджит (Симферополь)') if settings else 'Акъмесджит (Симферополь)'
    offset = settings.get('time_offset', 0) if settings else 0
    show_loc = bool(settings.get('show_location', 1)) if settings else True
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    
    text = (
        f"{_('location_title')}\n\n"
        f"{_('location_current')} <b>{current}</b>\n"
        f"{_('location_offset')} <b>{offset:+d} {_('minutes')}</b>\n"
    )
    
    if prayer_offsets and any(v != 0 for v in prayer_offsets.values()):
        text += f"{_('location_individual')} <b>{_('location_configured')}</b>\n"
    
    text += f"\n{_('location_select')}"
    
    await callback.message.edit_text(
        text,
        reply_markup=location_keyboard(current, show_loc, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_location_display")
async def toggle_location_display(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Переключение отображения названия города"""
    settings = await get_chat_settings(callback.message.chat.id)
    current = bool(settings.get('show_location', 1)) if settings else True
    await save_chat_settings(callback.message.chat.id, show_location=0 if current else 1)
    await callback.answer(_("changed"))
    await show_location(callback, state, _, lang)


@router.callback_query(F.data.startswith("set_loc_"))
async def set_location_from_list(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Установка города из списка"""
    try:
        idx = int(callback.data.replace("set_loc_", ""))
        if 0 <= idx < len(LOCATIONS):
            name, offset = LOCATIONS[idx]
            await save_chat_settings(
                callback.message.chat.id,
                location_name=name,
                time_offset=offset,
                prayer_offsets={}
            )
            await callback.answer(f"✅ {name} ({offset:+d} {_('minutes')})")
            await show_location(callback, state, _, lang)
        else:
            await callback.answer(_("error"), show_alert=True)
    except (ValueError, IndexError):
        await callback.answer(_("error"), show_alert=True)


# === Меню "Другая локация" ===

@router.callback_query(F.data == "custom_location")
async def custom_location_menu(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Меню другой локации"""
    await state.clear()
    await _show_custom_location_menu(callback.message.chat.id, callback.message, lang)
    await callback.answer()


# === Ввод названия ===

@router.callback_query(F.data == "enter_city_name")
async def enter_city_name(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Начать ввод названия города"""
    text = (
        f"{_('enter_city_title')}\n\n"
        f"<i>{_('enter_city_example')}</i>"
    )
    
    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(LocationStates.waiting_city_name)
    await state.update_data(menu_message_id=callback.message.message_id, lang=lang)
    await callback.answer()


@router.message(LocationStates.waiting_city_name)
async def process_city_name(message: Message, state: FSMContext, bot: Bot):
    """Обработка названия города"""
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    _ = lambda key: get_text(lang, key)
    
    name = message.text.strip()[:50]
    
    if not name:
        await message.answer(_("city_empty"))
        return
    
    await save_chat_settings(message.chat.id, location_name=name)
    
    # Удаляем сообщение пользователя
    try:
        await message.delete()
    except:
        pass
    
    menu_message_id = data.get('menu_message_id')
    
    await state.clear()
    
    if menu_message_id:
        try:
            settings = await get_chat_settings(message.chat.id)
            current_name = settings.get('location_name', name)
            general_offset = settings.get('time_offset', 0) if settings else 0
            prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
            
            text = (
                f"{_('custom_location_title')}\n\n"
                f"{_('custom_location_name')} <b>{current_name}</b> ✅\n"
                f"{_('custom_location_offset')} <b>{general_offset:+d} {_('minutes')}</b>\n"
            )
            
            if prayer_offsets and any(v != 0 for v in prayer_offsets.values()):
                text += f"🕌 {_('location_individual')} <b>{_('location_configured')}</b>\n"
            
            await bot.edit_message_text(
                text,
                chat_id=message.chat.id,
                message_id=menu_message_id,
                reply_markup=custom_location_menu_keyboard(lang),
                parse_mode="HTML"
            )
        except Exception:
            await message.answer(f"{_('city_set')} <b>{name}</b>", parse_mode="HTML")
    else:
        await message.answer(f"{_('city_set')} <b>{name}</b>", parse_mode="HTML")


# === Меню смещения ===

@router.callback_query(F.data == "offset_menu")
async def offset_menu(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Меню смещения времени"""
    await state.clear()
    await _show_offset_menu(callback.message.chat.id, callback.message, lang)
    await callback.answer()


# === Общее смещение ===

@router.callback_query(F.data == "offset_general")
async def offset_general(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Настройка общего смещения"""
    settings = await get_chat_settings(callback.message.chat.id)
    general_offset = settings.get('time_offset', 0) if settings else 0
    
    text = (
        f"{_('general_offset_title')}\n\n"
        f"{_('general_offset_current')} <b>{general_offset:+d} {_('minutes')}</b>\n\n"
        f"{_('offset_positive')}\n"
        f"{_('offset_negative')}\n\n"
        f"{_('offset_select')}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=general_offset_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_general_offset_"))
async def set_general_offset(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Установка общего смещения"""
    offset = int(callback.data.replace("set_general_offset_", ""))
    await save_chat_settings(callback.message.chat.id, time_offset=offset)
    await callback.answer(f"{_('offset_set')} {offset:+d} {_('minutes')}")
    await offset_menu(callback, state, _, lang)


@router.callback_query(F.data == "general_offset_manual")
async def general_offset_manual(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Ручной ввод общего смещения"""
    await callback.message.edit_text(
        _("enter_offset"),
        parse_mode="HTML"
    )
    await state.set_state(LocationStates.waiting_general_offset)
    await state.update_data(menu_message_id=callback.message.message_id, lang=lang)
    await callback.answer()


@router.message(LocationStates.waiting_general_offset)
async def process_general_offset(message: Message, state: FSMContext, bot: Bot):
    """Обработка ввода общего смещения"""
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    _ = lambda key: get_text(lang, key)
    
    try:
        offset = int(message.text.strip().replace("+", ""))
        
        if not (-120 <= offset <= 120):
            await message.answer(_("offset_range_error"))
            return
        
        await save_chat_settings(message.chat.id, time_offset=offset)
        
        # Удаляем сообщение пользователя
        try:
            await message.delete()
        except:
            pass
        
        menu_message_id = data.get('menu_message_id')
        await state.clear()
        
        if menu_message_id:
            try:
                await _show_offset_menu_by_id(message.chat.id, menu_message_id, bot, lang)
            except Exception:
                await message.answer(f"{_('offset_set')} {offset:+d} {_('minutes')}")
        else:
            await message.answer(f"{_('offset_set')} {offset:+d} {_('minutes')}")
        
    except ValueError:
        await message.answer(_("offset_number_error"))


async def _show_offset_menu_by_id(chat_id: int, message_id: int, bot: Bot, lang: str):
    """Показать меню смещения по ID сообщения"""
    _ = lambda key: get_text(lang, key)
    settings = await get_chat_settings(chat_id)
    general_offset = settings.get('time_offset', 0) if settings else 0
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    has_prayer_offsets = bool(prayer_offsets and any(v != 0 for v in prayer_offsets.values()))
    
    text = (
        f"{_('offset_title')}\n\n"
        f"{_('offset_general')} <b>{general_offset:+d} {_('minutes')}</b> ✅\n"
    )
    
    if has_prayer_offsets:
        text += f"{_('offset_individual_set')} <b>{_('location_configured')}</b>\n"
    
    text += (
        f"\n{_('offset_desc_general')}\n"
        f"{_('offset_desc_prayer')}"
    )
    
    await bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=offset_menu_keyboard(general_offset, has_prayer_offsets, lang),
        parse_mode="HTML"
    )


# === Смещение по намазам ===

@router.callback_query(F.data == "offset_by_prayer")
async def offset_by_prayer(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Настройка смещения по намазам"""
    await state.clear()
    await _show_prayer_offsets_menu(callback.message.chat.id, callback.message, lang)
    await callback.answer()


@router.callback_query(F.data.startswith("prayer_offset_") & ~F.data.startswith("prayer_offset_reset") & ~F.data.startswith("prayer_offset_manual"))
async def select_prayer_offset(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Выбор намаза для смещения"""
    prayer_key = callback.data.replace("prayer_offset_", "")
    
    settings = await get_chat_settings(callback.message.chat.id)
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    current_offset = prayer_offsets.get(prayer_key, 0)
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES['standard'])
    
    await state.update_data(current_prayer_key=prayer_key, lang=lang)
    
    text = (
        f"{_('offset_for').format(prayer=prayer_names[prayer_key])}\n\n"
        f"{_('general_offset_current')} <b>{current_offset:+d} {_('minutes')}</b>\n\n"
        f"{_('offset_select')}"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=prayer_offset_values_keyboard(prayer_key, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_prayer_offset_"))
async def set_prayer_offset(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
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
    await callback.answer(f"{_('offset_set')} {offset:+d} {_('minutes')}")
    await offset_by_prayer(callback, state, _, lang)


@router.callback_query(F.data.startswith("prayer_offset_manual_"))
async def prayer_offset_manual(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Ручной ввод смещения для намаза"""
    prayer_key = callback.data.replace("prayer_offset_manual_", "")
    await state.update_data(current_prayer_key=prayer_key, menu_message_id=callback.message.message_id, lang=lang)
    
    settings = await get_chat_settings(callback.message.chat.id)
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES['standard'])
    
    await callback.message.edit_text(
        f"{_('offset_for').format(prayer=prayer_names[prayer_key])}\n\n"
        f"{_('enter_offset').split(chr(10), 1)[1]}",  # Берём часть после заголовка
        parse_mode="HTML"
    )
    await state.set_state(LocationStates.waiting_prayer_offset)
    await callback.answer()


@router.message(LocationStates.waiting_prayer_offset)
async def process_prayer_offset(message: Message, state: FSMContext, bot: Bot):
    """Обработка ввода смещения для намаза"""
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    _ = lambda key: get_text(lang, key)
    
    try:
        offset = int(message.text.strip().replace("+", ""))
        
        if not (-120 <= offset <= 120):
            await message.answer(_("offset_range_error"))
            return
        
        prayer_key = data.get('current_prayer_key')
        menu_message_id = data.get('menu_message_id')
        
        if not prayer_key:
            await state.clear()
            await message.answer(_("error"))
            return
        
        settings = await get_chat_settings(message.chat.id)
        prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
        
        if offset == 0:
            prayer_offsets.pop(prayer_key, None)
        else:
            prayer_offsets[prayer_key] = offset
        
        await save_chat_settings(message.chat.id, prayer_offsets=prayer_offsets)
        
        # Удаляем сообщение пользователя
        try:
            await message.delete()
        except:
            pass
        
        await state.clear()
        
        if menu_message_id:
            try:
                await _show_prayer_offsets_menu_by_id(message.chat.id, menu_message_id, bot, lang)
            except Exception:
                await message.answer(f"{_('offset_set')} {offset:+d} {_('minutes')}")
        else:
            await message.answer(f"{_('offset_set')} {offset:+d} {_('minutes')}")
        
    except ValueError:
        await message.answer(_("offset_number_error"))


async def _show_prayer_offsets_menu_by_id(chat_id: int, message_id: int, bot: Bot, lang: str):
    """Показать меню смещения по намазам по ID сообщения"""
    _ = lambda key: get_text(lang, key)
    settings = await get_chat_settings(chat_id)
    prayer_offsets = settings.get('prayer_offsets', {}) if settings else {}
    prayer_names_style = settings.get('prayer_names_style', 'standard') if settings else 'standard'
    general_offset = settings.get('time_offset', 0) if settings else 0
    
    text = (
        f"{_('prayer_offset_title')}\n\n"
        f"{_('offset_general')} <b>{general_offset:+d} {_('minutes')}</b>\n\n"
        f"{_('prayer_offset_desc')}\n\n"
        f"{_('select_prayer')}"
    )
    
    await bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=prayer_offsets_keyboard(prayer_offsets, prayer_names_style, lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "prayer_offset_reset_all")
async def reset_all_prayer_offsets(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Сброс всех индивидуальных смещений"""
    await save_chat_settings(callback.message.chat.id, prayer_offsets={})
    await callback.answer(_("all_offsets_reset"))
    await offset_by_prayer(callback, state, _, lang)