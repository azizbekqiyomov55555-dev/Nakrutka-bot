from aiogram import Router
from aiogram.types import Message
from app.services.game_service import slot

router = Router()

@router.message(lambda m: m.text.startswith("/slot"))
async def slot_game(message: Message, db_user):
    bet = int(message.text.split()[1])
    result = await slot(db_user, bet)
    await message.answer(result)
