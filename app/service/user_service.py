from sqlalchemy import select

from app.db.models import User
from app.db.session import async_session_maker


async def create_user(tg_id: int, chat_id: int, username: str) -> User:
    async with async_session_maker() as session:
        user = User(tg_id=tg_id, chat_id=chat_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def get_user_or_raise(tg_id: int) -> User:
    async with async_session_maker() as session:
        query = select(User).where(User.tg_id == tg_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            return user

        raise ValueError("Пользователь не найден. Пожалуйста, введите команду /start")

async def get_or_create_user(tg_id: int, chat_id: int, username: str) -> User:
    try:
        user = await get_user_or_raise(tg_id=tg_id)
    except ValueError:
        user = await create_user(tg_id=tg_id, chat_id=chat_id, username=username)

    return user
