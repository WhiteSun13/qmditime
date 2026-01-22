from aiogram import Router, F
from aiogram.filters import ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated

router = Router()

# Обработчик события: Пользователь разблокировал бота (или добавил в группу)
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    """
    Срабатывает, когда пользователь разблокирует бота.
    Мы помечаем его как активного в базе данных.
    """
    # Импортируем функцию, которую мы создали в предыдущем шаге
    from database import set_chat_active_status
    
    await set_chat_active_status(event.chat.id, True)
    
    # Опционально: можно отправить сообщение "С возвращением!"
    # но лучше не спамить, просто тихо включить рассылку.
    print(f"Пользователь {event.chat.id} разблокировал бота. Статус восстановлен.")

# Обработчик события: Пользователь заблокировал бота
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    """
    Срабатывает мгновенно, когда пользователь блокирует бота.
    """
    from database import set_chat_active_status
    await set_chat_active_status(event.chat.id, False)
    print(f"Пользователь {event.chat.id} заблокировал бота.")