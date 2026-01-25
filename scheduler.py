from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pytz
import asyncio
from aiogram import Bot
from database import get_chats_with_daily_schedule, get_chats_with_reminders
from prayer_times import prayer_manager
from config import TIMEZONE, PRAYER_NAMES_STYLES
from broadcaster import send_safe_message 
from locales import get_text
import logging

logger = logging.getLogger(__name__)


class PrayerScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=TIMEZONE)
        self.tz = pytz.timezone(TIMEZONE)
    
    def start(self):
        """Запуск планировщика"""
        # Проверка ежедневных расписаний каждую минуту
        self.scheduler.add_job(
            self.check_daily_schedules,
            CronTrigger(minute='*'),
            id='daily_schedules',
            replace_existing=True
        )
        
        # Проверка напоминаний каждую минуту
        self.scheduler.add_job(
            self.check_reminders,
            CronTrigger(minute='*'),
            id='reminders',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Планировщик запущен")
    
    def stop(self):
        self.scheduler.shutdown()
        logger.info("Планировщик остановлен")
    
    async def check_daily_schedules(self):
        """Проверка и отправка ежедневных расписаний"""
        now = datetime.now(self.tz)
        current_time = now.strftime("%H:%M")
        
        chats = await get_chats_with_daily_schedule()
        
        # Фильтруем тех, кому нужно отправить прямо сейчас
        target_chats = [chat for chat in chats if chat.get('daily_schedule_time') == current_time]
        
        if not target_chats:
            return

        logger.info(f"Начинаем рассылку расписания для {len(target_chats)} чатов")
        
        # Запускаем рассылку в цикле
        count = 0
        for chat in target_chats:
            asyncio.create_task(self.process_daily_schedule_sending(chat))
            # Небольшая пауза, чтобы не убить API Telegram (примерно 20 сообщений в секунду)
            await asyncio.sleep(0.05) 
            count += 1
            
        logger.info(f"Задачи на рассылку созданы для {count} чатов")

    async def process_daily_schedule_sending(self, chat_settings: dict):
        """Подготовка данных и вызов безопасной отправки"""
        chat_id = chat_settings['chat_id']
        lang = chat_settings.get('language', 'ru')
        
        # Определяем дату
        today = datetime.now(self.tz).date()
        if chat_settings.get('schedule_day') == 'tomorrow':
            target_date = today + timedelta(days=1)
        else:
            target_date = today
        
        text = prayer_manager.format_schedule(
            target_date=target_date,
            general_offset=chat_settings.get('time_offset', 0),
            prayer_offsets=chat_settings.get('prayer_offsets', {}),
            location_name=chat_settings.get('location_name', 'Симферополь'),
            enabled_prayers=chat_settings.get('enabled_prayers'),
            show_location=bool(chat_settings.get('show_location', 1)),
            prayer_names_style=chat_settings.get('prayer_names_style', 'standard'),
            show_hijri=bool(chat_settings.get('show_hijri', 1)),
            hijri_style=chat_settings.get('hijri_style', 'cyrillic'),
            show_holidays=bool(chat_settings.get('show_holidays', 1)),
            lang=lang
        )
        
        # Используем безопасную отправку
        await send_safe_message(self.bot, chat_id, text)

    async def check_reminders(self):
        """Проверка и отправка напоминаний"""
        now = datetime.now(self.tz)
        today = now.date()
        
        chats = await get_chats_with_reminders()
        
        for chat in chats:
            await self.process_single_chat_reminder(chat, now, today)

    async def process_single_chat_reminder(self, chat: dict, now: datetime, today):
        """Логика проверки одного чата для напоминаний"""
        reminders = chat.get('reminders', {})
        if not reminders:
            return
        
        times = prayer_manager.get_adjusted_times(
            today,
            chat.get('time_offset', 0),
            chat.get('prayer_offsets', {})
        )
        
        if not times:
            return
        
        prayer_names_style = chat.get('prayer_names_style', 'standard')
        lang = chat.get('language', 'ru')
        
        for prayer_key, reminder_minutes in reminders.items():
            prayer_time_str = times.get(prayer_key)
            if not prayer_time_str:
                continue
            
            prayer_time = datetime.strptime(prayer_time_str, "%H:%M")
            prayer_datetime = now.replace(
                hour=prayer_time.hour,
                minute=prayer_time.minute,
                second=0,
                microsecond=0
            )
            
            # Время напоминания
            reminder_datetime = prayer_datetime - timedelta(minutes=reminder_minutes)
            
            # Проверяем нужно ли отправить напоминание (с точностью до минуты)
            if (reminder_datetime.hour == now.hour and 
                reminder_datetime.minute == now.minute):
                
                await self.send_reminder_safe(
                    chat['chat_id'],
                    prayer_key,
                    prayer_time_str,
                    reminder_minutes,
                    prayer_names_style,
                    lang
                )

    async def send_reminder_safe(
        self,
        chat_id: int,
        prayer_key: str,
        prayer_time: str,
        minutes_before: int,
        prayer_names_style: str = "standard",
        lang: str = "ru"
    ):
        """Подготовка текста и отправка напоминания"""
        prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES["standard"])
        prayer_name = prayer_names[prayer_key]
        
        if prayer_key == "sunrise":
            text = get_text(lang, "reminder_sunrise_soon", min=minutes_before, prayer=prayer_name, time=prayer_time)
        else:
            text = get_text(lang, "reminder_prayer_soon", min=minutes_before, prayer=prayer_name, time=prayer_time)
        
        # Используем безопасную отправку
        await send_safe_message(self.bot, chat_id, text)