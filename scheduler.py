from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pytz
from aiogram import Bot
from database import get_chats_with_daily_schedule, get_chats_with_reminders
from prayer_times import prayer_manager
from config import TIMEZONE, PRAYER_NAMES_STYLES
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
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Планировщик остановлен")
    
    async def check_daily_schedules(self):
        """Проверка и отправка ежедневных расписаний"""
        now = datetime.now(self.tz)
        current_time = now.strftime("%H:%M")
        
        chats = await get_chats_with_daily_schedule()
        
        for chat in chats:
            if chat.get('daily_schedule_time') == current_time:
                try:
                    await self.send_daily_schedule(chat)
                except Exception as e:
                    logger.error(f"Ошибка отправки расписания в чат {chat['chat_id']}: {e}")
    
    async def send_daily_schedule(self, chat_settings: dict):
        """Отправка ежедневного расписания"""
        chat_id = chat_settings['chat_id']
        
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
            show_holidays=bool(chat_settings.get('show_holidays', 1))
        )
        
        await self.bot.send_message(chat_id, text, parse_mode="HTML")
        logger.info(f"Отправлено ежедневное расписание в чат {chat_id}")
    
    async def check_reminders(self):
        """Проверка и отправка напоминаний"""
        now = datetime.now(self.tz)
        today = now.date()
        
        chats = await get_chats_with_reminders()
        
        for chat in chats:
            reminders = chat.get('reminders', {})
            if not reminders:
                continue
            
            times = prayer_manager.get_adjusted_times(
                today,
                chat.get('time_offset', 0),
                chat.get('prayer_offsets', {})
            )
            
            if not times:
                continue
            
            prayer_names_style = chat.get('prayer_names_style', 'standard')
            
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
                    try:
                        await self.send_reminder(
                            chat['chat_id'],
                            prayer_key,
                            prayer_time_str,
                            reminder_minutes,
                            prayer_names_style
                        )
                    except Exception as e:
                        logger.error(f"Ошибка отправки напоминания в чат {chat['chat_id']}: {e}")
    
    async def send_reminder(
        self,
        chat_id: int,
        prayer_key: str,
        prayer_time: str,
        minutes_before: int,
        prayer_names_style: str = "standard"
    ):
        """Отправка напоминания о намазе"""
        prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES["standard"])
        prayer_name = prayer_names[prayer_key]
        if (prayer_key == "sunrise"):
            text = (
                f"🔔 <b>Скоро восход солнца!</b>\n\n"
                f"Через <b>{minutes_before} мин.</b> наступит:\n"
                f"{prayer_name} — <b>{prayer_time}</b>"
            )
        else:
            text = (
                f"🔔 <b>Скоро намаз!</b>\n\n"
                f"Через <b>{minutes_before} мин.</b> наступит:\n"
                f"{prayer_name} — <b>{prayer_time}</b>"
            )
        
        await self.bot.send_message(chat_id, text, parse_mode="HTML")
        logger.info(f"Отправлено напоминание о {prayer_key} в чат {chat_id}")