from aiogram import Router
from . import start, settings, schedule, reminders, location, status

def setup_routers() -> Router:
    """Настройка роутеров"""
    router = Router()
    
    router.include_router(start.router)
    router.include_router(settings.router)
    router.include_router(schedule.router)
    router.include_router(reminders.router)
    router.include_router(location.router)
    router.include_router(status.router)
    
    return router