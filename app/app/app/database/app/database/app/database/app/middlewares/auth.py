from aiogram import BaseMiddleware
from app.database.engine import SessionLocal
from app.database.models import User
from app.config import settings
from sqlalchemy import select

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        async with SessionLocal() as session:
            result = await session.execute(select(User).where(User.id == event.from_user.id))
            user = result.scalar_one_or_none()

            if not user:
                user = User(
                    id=event.from_user.id,
                    is_admin=(event.from_user.id == settings.ADMIN_ID)
                )
                session.add(user)
                await session.commit()

            data["db_user"] = user
        return await handler(event, data)
