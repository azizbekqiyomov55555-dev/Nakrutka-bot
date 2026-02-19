from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message(lambda m: m.text == "/start")
async def start(message: Message):
    await message.answer("🔥 MegaBot ishga tushdi")
