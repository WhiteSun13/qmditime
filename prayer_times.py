import csv
from datetime import datetime, timedelta, date
from typing import Optional, Dict
import pytz
from hijri_converter import Hijri, Gregorian
from config import (
    CSV_PATH, TIMEZONE, PRAYER_NAMES_STYLES, PRAYER_KEYS,
    HIJRI_MONTHS, HOLIDAYS, RAMADAN_PERIODS
)


class PrayerTimesManager:
    def __init__(self):
        self.data: Dict[date, Dict[str, str]] = {}
        self.tz = pytz.timezone(TIMEZONE)
        self.load_data()
    
    def load_data(self):
        """Загрузка CSV"""
        self.data = {}
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    d = datetime.strptime(row['date'].strip(), "%Y-%m-%d").date()
                    self.data[d] = {key: row[key].strip() for key in PRAYER_KEYS}
                except:
                    pass
        print(f"Загружено {len(self.data)} дней")
    
    def get_times_for_date(self, target_date: date) -> Optional[Dict[str, str]]:
        """Получить времена намазов на определённую дату"""
        return self.data.get(target_date)
    
    def apply_offset(self, time_str: str, offset_minutes: int) -> str:
        """Применить смещение к времени"""
        time_obj = datetime.strptime(time_str, "%H:%M")
        time_obj += timedelta(minutes=offset_minutes)
        return time_obj.strftime("%H:%M")
    
    def get_adjusted_times(
        self,
        target_date: date,
        general_offset: int = 0,
        prayer_offsets: Dict[str, int] = None
    ) -> Optional[Dict[str, str]]:
        """Получить времена с учётом смещений"""
        times = self.get_times_for_date(target_date)
        if not times:
            return None
        
        prayer_offsets = prayer_offsets or {}
        
        adjusted = {}
        for prayer, time in times.items():
            total_offset = general_offset + prayer_offsets.get(prayer, 0)
            adjusted[prayer] = self.apply_offset(time, total_offset)
        
        return adjusted
    
    def get_hijri_date(self, gregorian_date: date) -> tuple:
        """Получить дату по хиджри"""
        hijri = Gregorian(
            gregorian_date.year,
            gregorian_date.month,
            gregorian_date.day
        ).to_hijri()
        return hijri.day, hijri.month, hijri.year
    
    def format_hijri_date(self, gregorian_date: date, style: str = "cyrillic") -> str:
        """Форматировать дату хиджри"""
        day, month, year = self.get_hijri_date(gregorian_date)
        months = HIJRI_MONTHS.get(style, HIJRI_MONTHS["cyrillic"])
        month_name = months[month] if month < len(months) else months[0]
        return f"{day} {month_name} {year} х."
    
    def get_holiday(self, target_date: date) -> Optional[Dict]:
        """Получить праздник на дату"""
        year_holidays = HOLIDAYS.get(target_date.year, {})
        return year_holidays.get((target_date.month, target_date.day))
    
    def get_tomorrow_holiday(self, target_date: date) -> Optional[Dict]:
        """Получить праздник на завтра (для напоминания)"""
        tomorrow = target_date + timedelta(days=1)
        return self.get_holiday(tomorrow)
    
    def get_ramadan_countdown(self, target_date: date) -> Optional[Dict]:
        """Получить обратный отсчёт до/во время Рамазана"""
        ramadan = RAMADAN_PERIODS.get(target_date.year)
        if not ramadan:
            return None
        
        start = ramadan["start"]
        end = ramadan["end"]
        
        if target_date < start:
            days_until = (start - target_date).days
            return {
                "type": "before",
                "days": days_until,
                "text": f"🌙 До начала Рамазана: {days_until} дн."
            }
        elif target_date < end:
            days_until_end = (end - target_date).days
            day_of_ramadan = (target_date - start).days + 1
            return {
                "type": "during",
                "day": day_of_ramadan,
                "days_left": days_until_end,
                "text": f"🌙 Рамазан: {day_of_ramadan}-й день (осталось {days_until_end} дн.)"
            }
        
        return None
    
    def format_schedule(
        self,
        target_date: date,
        general_offset: int = 0,
        prayer_offsets: Dict[str, int] = None,
        location_name: str = "Симферополь",
        enabled_prayers: list = None,
        show_location: bool = True,
        prayer_names_style: str = "standard",
        show_hijri: bool = True,
        hijri_style: str = "cyrillic",
        show_holidays: bool = True
    ) -> str:
        """Форматированный вывод расписания"""
        times = self.get_adjusted_times(target_date, general_offset, prayer_offsets)
        
        if not times:
            return "❌ Расписание на эту дату не найдено"
        
        enabled_prayers = enabled_prayers or PRAYER_KEYS
        prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES["standard"])
        prayer_offsets = prayer_offsets or {}
        
        # Форматируем григорианскую дату
        months_ru = [
            "", "января", "февраля", "марта", "апреля", "мая", "июня",
            "июля", "августа", "сентября", "октября", "ноября", "декабря"
        ]
        weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресение"]
        
        date_str = f"{target_date.day} {months_ru[target_date.month]} {target_date.year}"
        weekday = weekdays[target_date.weekday()]
        
        text = f"🕌 <b>Расписание намаза</b>\n"
        
        if show_location and location_name:
            text += f"📍 {location_name}\n"
        
        text += f"📅 {date_str} ({weekday})\n"
        
        # Хиджри дата
        if show_hijri:
            hijri_str = self.format_hijri_date(target_date, hijri_style)
            text += f"🗓 {hijri_str}\n"
        
        text += "━" * 20 + "\n"
        
        # Времена намазов с индивидуальными смещениями
        for prayer in PRAYER_KEYS:
            if prayer in enabled_prayers:
                individual_offset = prayer_offsets.get(prayer, 0)
                if individual_offset != 0:
                    offset_text = f" <i>({individual_offset:+d})</i>"
                else:
                    offset_text = ""
                text += f"{prayer_names[prayer]} — <b>{times[prayer]}</b>{offset_text}\n"
        
        # Праздник/особый день
        if show_holidays:
            holiday = self.get_holiday(target_date)
            if holiday:
                emoji = "🌟" if holiday["type"] == "holiday" else "✨" if holiday.get("night") else "📿"
                if holiday.get("night"):
                    prev_date = target_date - timedelta(days=1)
                    if prev_date.month == target_date.month:
                        date_range = f" ({prev_date.day}-{target_date.day})"
                    else:
                        date_range = f" ({prev_date.day} {months_ru[prev_date.month]} - {target_date.day} {months_ru[target_date.month]})"
                    text += f"\n{emoji} <b>{holiday['name']}</b>{date_range}\n"
                else:
                    text += f"\n{emoji} <b>{holiday['name']}</b>\n"
            
            tomorrow_holiday = self.get_tomorrow_holiday(target_date)
            if tomorrow_holiday:
                if tomorrow_holiday.get("night"):
                    next_date = target_date - timedelta(days=1)
                    if next_date.month == target_date.month:
                        date_range = f" ({target_date.day}-{next_date.day})"
                    else:
                        date_range = f" ({target_date.day} {months_ru[target_date.month]} - {next_date.day} {months_ru[next_date.month]})"
                    text += f"\n <i>✨ В эту ночь: {tomorrow_holiday['name']}{date_range}</i>\n"
                else:
                    text += f"\n🔔 <i>Завтра: {tomorrow_holiday['name']}</i>\n"
            
            ramadan = self.get_ramadan_countdown(target_date)
            if ramadan and ramadan.get("days", 0) <= 60:
                text += f"\n{ramadan['text']}\n"
        
        # Информация о смещениях
        has_prayer_offsets = bool(prayer_offsets and any(v != 0 for v in prayer_offsets.values()))
        
        if general_offset != 0 or has_prayer_offsets:
            text += "\n"
            if general_offset != 0:
                sign = "+" if general_offset > 0 else ""
                text += f"⏱ <i>Время скорректировано на {sign}{general_offset} мин.</i>"
            if has_prayer_offsets:
                if general_offset != 0:
                    text += "\n"
                text += f"<i>Индивидуальные смещения применены</i>"
        
        return text
    
    def get_next_prayer(
        self,
        general_offset: int = 0,
        prayer_offsets: Dict[str, int] = None
    ) -> Optional[tuple]:
        """Получить следующий намаз"""
        now = datetime.now(self.tz)
        today = now.date()
        current_time = now.strftime("%H:%M")
        
        times = self.get_adjusted_times(today, general_offset, prayer_offsets)
        if not times:
            return None
        
        for prayer in PRAYER_KEYS:
            if times[prayer] > current_time:
                return (prayer, times[prayer], today)
        
        tomorrow = today + timedelta(days=1)
        times = self.get_adjusted_times(tomorrow, general_offset, prayer_offsets)
        if times:
            return (PRAYER_KEYS[0], times[PRAYER_KEYS[0]], tomorrow)
        
        return None


# Глобальный экземпляр
prayer_manager = PrayerTimesManager()