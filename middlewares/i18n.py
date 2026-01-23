from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from database import get_chat_settings, save_chat_settings
from locales import get_text

class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        
        user = data.get('event_from_user')
        if not user:
            return await handler(event, data)

        # Получаем настройки из БД
        settings = await get_chat_settings(user.id)
        
        # Если настроек нет, создаем (дефолт ru)
        if not settings:
            await save_chat_settings(user.id, 'private')
            lang = 'ru'
        else:
            lang = settings.get('language', 'ru')

        # Функция-хелпер для перевода, которую мы передадим в хендлер
        def _(key: str):
            return get_text(lang, key)

        # Передаем язык и функцию перевода в data
        data['lang'] = lang
        data['_'] = _
        
        return await handler(event, data)