from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from keyboards.inline import cancel_keyboard, help_keyboard
from config import ADMIN_ID

router = Router()

class FeedbackStates(StatesGroup):
    waiting_message = State()

# === Пользовательская часть ===

@router.callback_query(F.data == "feedback")
async def start_feedback(callback: CallbackQuery, state: FSMContext):
    """Начало ввода сообщения разработчику"""
    await callback.message.edit_text(
        "✍️ <b>Обратная связь</b>\n\n"
        "Напишите ваше сообщение, вопрос или предложение. Вложения работают (фото, аудио, видеофайлы, голосовое сообщение, видео-сообщение)\n"
        "Мы постараемся ответить вам в ближайшее время.",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(FeedbackStates.waiting_message)
    await callback.answer()

@router.callback_query(F.data == "cancel_feedback")
async def cancel_feedback(callback: CallbackQuery, state: FSMContext, _: callable, lang: str):
    """Отмена ввода - возвращает в раздел Помощь"""
    await state.clear()
    
    # Вызываем ту же функцию, что и при нажатии кнопки help
    from handlers.start import show_help
    await show_help(callback, _, lang)

@router.message(FeedbackStates.waiting_message)
async def process_feedback_message(message: Message, state: FSMContext, bot: Bot):
    """Обработка отправки сообщения админам"""
    
    # Формируем сообщение для админа
    user_info = f"👤 От: {message.from_user.full_name} (@{message.from_user.username})\n🆔 Ответить: <code>/reply {message.from_user.id} </code>"
    text_to_admin = (
        f"📩 <b>Новое сообщение</b>\n\n"
        f"{user_info}\n\n"
        f"📄 Текст:\n{message.text or message.caption or '[Медиафайл]'}"
    )

    # Отправляем всем админам
    for admin_id in ADMIN_ID:
        try:
            # Отправляем инфо
            await bot.send_message(admin_id, text_to_admin, parse_mode="HTML")
            
            # Пересылаем само сообщение (чтобы видеть фото/голос и можно было быстро ответить)
            # Но если у юзера закрыта пересылка, ID мы увидим выше в тексте
            await message.forward(chat_id=admin_id)
            
        except Exception as e:
            print(f"Не удалось отправить админу {admin_id}: {e}")

    await message.answer(
        "✅ <b>Сообщение отправлено!</b>\nСпасибо за обратную связь.",
        reply_markup=help_keyboard(),
        parse_mode="HTML"
    )
    await state.clear()

# === Админская часть (ответ пользователю) ===

@router.message(Command("reply"))
async def cmd_reply(message: Message, bot: Bot):
    """
    Команда для ответа пользователю: /reply ID ТЕКСТ
    Пример: /reply 123456789 Спасибо, исправим!
    """
    if message.from_user.id not in ADMIN_ID:
        return

    try:
        # Разбиваем сообщение на части: команда, ID, текст
        parts = message.text.split(maxsplit=2)
        
        if len(parts) < 3:
            await message.answer("⚠️ Ошибка формата.\nИспользуйте: <code>/reply ID ТЕКСТ</code>")
            return

        user_id = int(parts[1])
        reply_text = parts[2]

        # Отправляем ответ пользователю
        await bot.send_message(
            user_id,
            f"📨 <b>Ответ от разработчика:</b>\n\n{reply_text}",
            parse_mode="HTML"
        )
        
        await message.answer(f"✅ Ответ отправлен пользователю {user_id}")

    except ValueError:
        await message.answer("⚠️ ID пользователя должен быть числом.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке: {e}")