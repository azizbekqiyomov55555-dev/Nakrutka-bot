from aiogram import Router
from aiogram.types import Message
from app.config import settings

router = Router()

@router.message(lambda m: m.text == "/admin")
async def admin(message: Message):
    if message.from_user.id != settings.ADMIN_ID:
        return
    await message.answer("Admin panel")
