from aiogram import Router
from . import start, settings, schedule, reminders

def setup_routers() -> Router:
    """Настройка роутеров"""
    router = Router()
    
    router.include_router(start.router)
    router.include_router(settings.router)
    router.include_router(schedule.router)
    router.include_router(reminders.router)
    
    return router