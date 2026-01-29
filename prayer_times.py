import csv
from datetime import datetime, timedelta, date
from typing import Optional, Dict
import pytz
from hijri_converter import Hijri, Gregorian
from config import (
    CSV_PATH, TIMEZONE, PRAYER_NAMES_STYLES, PRAYER_KEYS,
    HIJRI_MONTHS, HOLIDAYS, RAMADAN_PERIODS
)
from locales import get_text, get_weekday, get_month

# Карта начал месяцев Хиджры для 2026 года по календарю ДУМК
# Ключ: Дата григорианского календаря (начало месяца)
# Значение: (Месяц Хиджры, Год Хиджры)
HIJRI_2026_MAP = {
    date(2025, 12, 21): (7, 1447),   # Реджеб
    date(2026, 1, 20):  (8, 1447),   # Шабан
    date(2026, 2, 19):  (9, 1447),   # Рамазан
    date(2026, 3, 20):  (10, 1447),  # Шевваль
    date(2026, 4, 19):  (11, 1447),  # Зилькаде
    date(2026, 5, 18):  (12, 1447),  # Зильхидждже
    date(2026, 6, 16):  (1, 1448),   # Мухаррем (Новый год)
    date(2026, 7, 16):  (2, 1448),   # Сефер
    date(2026, 8, 14):  (3, 1448),   # Ребиуль-эвель
    date(2026, 9, 13):  (4, 1448),   # Ребиуль-ахыр
    date(2026, 10, 12): (5, 1448),   # Джумазиель-эвель
    date(2026, 11, 11): (6, 1448),   # Джумазиель-ахыр
    date(2026, 12, 10): (7, 1448),   # Реджеб
}

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
    
    def _get_hijri_date_algo(self, gregorian_date: date) -> tuple:
        """Старый метод (алгоритмический расчет)"""
        hijri = Gregorian(
            gregorian_date.year,
            gregorian_date.month,
            gregorian_date.day
        ).to_hijri()
        return hijri.day, hijri.month, hijri.year

    def get_hijri_date(self, gregorian_date: date) -> tuple:
        """Получить дату по хиджри (сначала пробуем карту 2026, потом алгоритм)"""
        
        # Пытаемся найти в карте
        if gregorian_date.year == 2026 or (gregorian_date.year == 2025 and gregorian_date.month == 12):
            # Сортируем даты начала месяцев в обратном порядке
            sorted_starts = sorted(HIJRI_2026_MAP.keys(), reverse=True)
            
            for start_date in sorted_starts:
                if gregorian_date >= start_date:
                    h_month, h_year = HIJRI_2026_MAP[start_date]
                    # Разница в днях + 1 (так как первый день это 1-е число)
                    h_day = (gregorian_date - start_date).days + 1
                    return h_day, h_month, h_year

        # Если даты нет в карте, используем старую функцию
        return self._get_hijri_date_algo(gregorian_date)

    def _to_arabic_numerals(self, number: int) -> str:
        """Преобразование чисел в восточно-арабские цифры (٠-٩)"""
        table = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
        return str(number).translate(table)
    
    def format_hijri_date(self, gregorian_date: date, style: str = "translit", lang: str = "ru") -> str:
        """Форматировать дату хиджри"""
        day, month, year = self.get_hijri_date(gregorian_date)
        
        # Определяем реальный стиль месяцев
        if style == "arabic":
            month_style = "arabic"
        else:
            # Транслит - определяем по языку
            if lang == "crh_lat":
                month_style = "latin"
            else:
                # ru, crh_cyr -> кириллица
                month_style = "cyrillic"
        
        months = HIJRI_MONTHS.get(month_style, HIJRI_MONTHS["cyrillic"])
        month_name = months[month] if month < len(months) else months[0]
        
        # ЕСЛИ стиль арабский - конвертируем цифры
        if style == "arabic":
            day_str = self._to_arabic_numerals(day)
            year_str = self._to_arabic_numerals(year)
            return f"{day_str} {month_name} {year_str}"
            
        return f"{day} {month_name} {year}"
    
    def get_holiday(self, target_date: date) -> Optional[Dict]:
        """Получить праздник на дату"""
        year_holidays = HOLIDAYS.get(target_date.year, {})
        return year_holidays.get((target_date.month, target_date.day))
    
    def get_tomorrow_holiday(self, target_date: date) -> Optional[Dict]:
        """Получить праздник на завтра (для напоминания)"""
        tomorrow = target_date + timedelta(days=1)
        return self.get_holiday(tomorrow)
    
    def get_ramadan_countdown(self, target_date: date, lang: str = "ru") -> Optional[Dict]:
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
                "text": get_text(lang, "ramadan_before", days=days_until)
            }
        elif target_date < end:
            days_until_end = (end - target_date).days
            day_of_ramadan = (target_date - start).days + 1
            return {
                "type": "during",
                "day": day_of_ramadan,
                "days_left": days_until_end,
                "text": get_text(lang, "ramadan_during", day=day_of_ramadan, days_left=days_until_end)
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
        hijri_style: str = "translit",
        show_holidays: bool = True,
        lang: str = "ru"
    ) -> str:
        """Форматированный вывод расписания"""
        times = self.get_adjusted_times(target_date, general_offset, prayer_offsets)
        
        if not times:
            return get_text(lang, "schedule_not_found")
        
        enabled_prayers = enabled_prayers or PRAYER_KEYS
        prayer_names = PRAYER_NAMES_STYLES.get(prayer_names_style, PRAYER_NAMES_STYLES["standard"])
        prayer_offsets = prayer_offsets or {}
        
        # Форматируем григорианскую дату
        month_name = get_month(lang, target_date.month)
        weekday = get_weekday(lang, target_date.weekday())
        
        date_str = f"{target_date.day} {month_name} {target_date.year}"
        
        text = get_text(lang, "schedule_header") + "\n"
        
        if show_location and location_name:
            text += f"📍 {location_name}\n"
        
        text += f"📅 {date_str} ({weekday})\n"
        
        # Хиджри дата
        if show_hijri:
            hijri_str = self.format_hijri_date(target_date, hijri_style, lang)
            # Добавляем \u200e для выравнивания
            text += f"🗓 \u200e{hijri_str}\n"
        
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
                        prev_month = get_month(lang, prev_date.month)
                        curr_month = get_month(lang, target_date.month)
                        date_range = f" ({prev_date.day} {prev_month} - {target_date.day} {curr_month})"
                    text += f"\n{emoji} <b>{holiday['name']}</b>{date_range}\n"
                else:
                    text += f"\n{emoji} <b>{holiday['name']}</b>\n"
            
            tomorrow_holiday = self.get_tomorrow_holiday(target_date)
            if tomorrow_holiday:
                if tomorrow_holiday.get("night"):
                    next_date = target_date + timedelta(days=1)
                    if next_date.month == target_date.month:
                        date_range = f" ({target_date.day}-{next_date.day})"
                    else:
                        curr_month = get_month(lang, target_date.month)
                        next_month = get_month(lang, next_date.month)
                        date_range = f" ({target_date.day} {curr_month} - {next_date.day} {next_month})"
                    tonight_label = get_text(lang, "tonight_label")
                    text += f"\n <i>✨ {tonight_label} {tomorrow_holiday['name']}{date_range}</i>\n"
                else:
                    tomorrow_label = get_text(lang, "tomorrow_label")
                    text += f"\n🔔 <i>{tomorrow_label} {tomorrow_holiday['name']}</i>\n"
            
            ramadan = self.get_ramadan_countdown(target_date, lang)
            if ramadan and ramadan.get("days", 0) <= 60:
                text += f"\n{ramadan['text']}\n"
        
        # Информация о смещениях
        has_prayer_offsets = bool(prayer_offsets and any(v != 0 for v in prayer_offsets.values()))
        
        if general_offset != 0 or has_prayer_offsets:
            text += "\n"
            if general_offset != 0:
                sign = "+" if general_offset > 0 else ""
                text += get_text(lang, "time_adjusted", offset=f"{sign}{general_offset}")
            if has_prayer_offsets:
                if general_offset != 0:
                    text += "\n"
                text += get_text(lang, "individual_offsets_applied")
        
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