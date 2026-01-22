import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramBadRequest
from database import set_chat_active_status

logger = logging.getLogger(__name__)

async def send_safe_message(bot: Bot, chat_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Безопасная отправка сообщения.
    Возвращает True, если отправлено успешно, иначе False.
    """
    try:
        await bot.send_message(
            chat_id, 
            text, 
            parse_mode="HTML", 
            disable_notification=disable_notification
        )
        return True
        
    except TelegramRetryAfter as e:
        # Если Telegram говорит "подожди", мы ждем и пробуем снова
        logger.warning(f"Flood limit exceeded for {chat_id}. Sleep {e.retry_after} seconds.")
        await asyncio.sleep(e.retry_after)
        return await send_safe_message(bot, chat_id, text, disable_notification)
        
    except TelegramForbiddenError:
        # Пользователь заблокировал бота
        logger.info(f"Chat {chat_id} blocked the bot. Deactivating.")
        await set_chat_active_status(chat_id, False)
        
    except TelegramBadRequest as e:
        logger.error(f"Bad request for {chat_id}: {e}")
        
    except Exception as e:
        logger.error(f"Unexpected error for {chat_id}: {e}")
        
    return False