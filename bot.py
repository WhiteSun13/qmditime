import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database import init_db
from handlers import setup_routers
from scheduler import PrayerScheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    # Инициализация БД
    await init_db()
    
    # Создание бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создание диспетчера
    dp = Dispatcher()
    
    # Подключение роутеров
    dp.include_router(setup_routers())
    
    # Запуск планировщика
    scheduler = PrayerScheduler(bot)
    scheduler.start()
    
    logger.info("Бот запущен")
    
    try:
        # Удаление webhook и запуск polling
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, polling_timeout=60)
    finally:
        scheduler.stop()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())