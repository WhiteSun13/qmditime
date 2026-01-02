import aiosqlite
import json
from config import DATABASE_PATH, PRAYER_KEYS
from typing import Optional, Dict, Any

async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Таблица настроек чатов
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_settings (
                chat_id INTEGER PRIMARY KEY,
                chat_type TEXT DEFAULT 'private',
                is_active INTEGER DEFAULT 1,
                
                -- Время ежедневной отправки расписания (NULL = не отправлять)
                daily_schedule_time TEXT DEFAULT NULL,
                
                -- Какой день показывать: 'today' или 'tomorrow'
                schedule_day TEXT DEFAULT 'today',
                
                -- Общее смещение времени в минутах
                time_offset INTEGER DEFAULT 0,
                
                -- Индивидуальные смещения для каждого намаза (JSON)
                prayer_offsets TEXT DEFAULT '{}',
                
                -- Напоминания за N минут (JSON)
                reminders TEXT DEFAULT '{}',
                
                -- Включенные намазы (JSON массив)
                enabled_prayers TEXT DEFAULT '["fajr","sunrise","dhuhr","asr","maghrib","isha"]',
                
                -- Название локации
                location_name TEXT DEFAULT 'Симферополь',
                
                -- Показывать ли локацию в расписании
                show_location INTEGER DEFAULT 1,
                
                -- Стиль названий намазов: standard, crimean_cyrillic, crimean_latin
                prayer_names_style TEXT DEFAULT 'standard',
                
                -- Стиль хиджри месяцев: cyrillic, latin
                hijri_style TEXT DEFAULT 'cyrillic',
                
                -- Показывать ли дату хиджри
                show_hijri INTEGER DEFAULT 1,
                
                -- Показывать ли праздники
                show_holidays INTEGER DEFAULT 1,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Миграция: добавление новых колонок если их нет
        try:
            await db.execute("ALTER TABLE chat_settings ADD COLUMN show_location INTEGER DEFAULT 1")
        except:
            pass
        try:
            await db.execute("ALTER TABLE chat_settings ADD COLUMN prayer_names_style TEXT DEFAULT 'standard'")
        except:
            pass
        try:
            await db.execute("ALTER TABLE chat_settings ADD COLUMN hijri_style TEXT DEFAULT 'cyrillic'")
        except:
            pass
        try:
            await db.execute("ALTER TABLE chat_settings ADD COLUMN show_hijri INTEGER DEFAULT 1")
        except:
            pass
        try:
            await db.execute("ALTER TABLE chat_settings ADD COLUMN show_holidays INTEGER DEFAULT 1")
        except:
            pass
        
        await db.commit()


async def get_chat_settings(chat_id: int) -> Optional[Dict[str, Any]]:
    """Получить настройки чата"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM chat_settings WHERE chat_id = ?", (chat_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                settings = dict(row)
                settings['prayer_offsets'] = json.loads(settings.get('prayer_offsets') or '{}')
                settings['reminders'] = json.loads(settings.get('reminders') or '{}')
                settings['enabled_prayers'] = json.loads(settings.get('enabled_prayers') or '[]')
                # Установка значений по умолчанию для новых полей
                settings.setdefault('show_location', 1)
                settings.setdefault('prayer_names_style', 'standard')
                settings.setdefault('hijri_style', 'cyrillic')
                settings.setdefault('show_hijri', 1)
                settings.setdefault('show_holidays', 1)
                return settings
            return None


async def save_chat_settings(chat_id: int, chat_type: str = 'private', **kwargs):
    """Сохранить настройки чата"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        existing = await get_chat_settings(chat_id)
        
        if existing:
            updates = []
            values = []
            for key, value in kwargs.items():
                if key in ['prayer_offsets', 'reminders', 'enabled_prayers']:
                    value = json.dumps(value)
                updates.append(f"{key} = ?")
                values.append(value)
            
            if updates:
                values.append(chat_id)
                await db.execute(
                    f"UPDATE chat_settings SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?",
                    values
                )
        else:
            for key in ['prayer_offsets', 'reminders', 'enabled_prayers']:
                if key in kwargs:
                    kwargs[key] = json.dumps(kwargs[key])
            
            columns = ['chat_id', 'chat_type'] + list(kwargs.keys())
            placeholders = ['?'] * len(columns)
            values = [chat_id, chat_type] + list(kwargs.values())
            
            await db.execute(
                f"INSERT INTO chat_settings ({', '.join(columns)}) VALUES ({', '.join(placeholders)})",
                values
            )
        
        await db.commit()


async def get_all_active_chats() -> list:
    """Получить все активные чаты"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM chat_settings WHERE is_active = 1"
        ) as cursor:
            rows = await cursor.fetchall()
            result = []
            for row in rows:
                settings = dict(row)
                settings['prayer_offsets'] = json.loads(settings.get('prayer_offsets') or '{}')
                settings['reminders'] = json.loads(settings.get('reminders') or '{}')
                settings['enabled_prayers'] = json.loads(settings.get('enabled_prayers') or '[]')
                result.append(settings)
            return result


async def get_chats_with_daily_schedule() -> list:
    """Получить чаты с включенной ежедневной отправкой"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM chat_settings WHERE is_active = 1 AND daily_schedule_time IS NOT NULL"
        ) as cursor:
            rows = await cursor.fetchall()
            result = []
            for row in rows:
                settings = dict(row)
                settings['prayer_offsets'] = json.loads(settings.get('prayer_offsets') or '{}')
                settings['reminders'] = json.loads(settings.get('reminders') or '{}')
                settings['enabled_prayers'] = json.loads(settings.get('enabled_prayers') or '[]')
                result.append(settings)
            return result


async def get_chats_with_reminders() -> list:
    """Получить чаты с включенными напоминаниями"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM chat_settings WHERE is_active = 1 AND reminders != '{}'"
        ) as cursor:
            rows = await cursor.fetchall()
            result = []
            for row in rows:
                settings = dict(row)
                settings['prayer_offsets'] = json.loads(settings.get('prayer_offsets') or '{}')
                settings['reminders'] = json.loads(settings.get('reminders') or '{}')
                settings['enabled_prayers'] = json.loads(settings.get('enabled_prayers') or '[]')
                result.append(settings)
            return result