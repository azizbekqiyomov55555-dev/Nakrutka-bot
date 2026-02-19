import os
import random
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.db import init_db, add_user, get_user, update_balance
from app.keyboards import main_menu

TOKEN = ("8318931210:AAFJLBgfF2_reXxXWpWjb8NjsuveWxYIVjY")  # Railway env ga qo'yiladi

bot = Bot(token=TOKEN)
dp = Dispatcher()

# O'yin rejimini saqlash uchun vaqtinchalik dict
user_game_state = {}

@dp.message(CommandStart())
async def start_handler(message: Message):
    await add_user(message.from_user.id)
    await message.answer(
        "🎰 Casino botga xush kelibsiz!",
        reply_markup=main_menu()
    )

@dp.message(F.text == "👤 Profil")
async def profile_handler(message: Message):
    user = await get_user(message.from_user.id)
    balance = user[0] if user else 0
    await message.answer(f"💰 Balans: {balance} coin")

@dp.message(F.text == "🎮 Coin Flip")
async def coinflip_start(message: Message):
    user_game_state[message.from_user.id] = "waiting_bet"
    await message.answer("💵 Stavka miqdorini kiriting (masalan 100):")

@dp.message()
async def handle_bet(message: Message):
    user_id = message.from_user.id

    if user_game_state.get(user_id) != "waiting_bet":
        return

    if not message.text.isdigit():
        await message.answer("❌ Iltimos, faqat raqam kiriting.")
        return

    bet = int(message.text)
    user = await get_user(user_id)

    if not user:
        return

    balance = user[0]

    if bet <= 0:
        await message.answer("❌ Stavka 0 dan katta bo‘lishi kerak.")
        return

    if bet > balance:
        await message.answer("❌ Balans yetarli emas!")
        return

    # 48% win, 52% lose (profit uchun)
    result = random.choices(["win", "lose"], weights=[48, 52])[0]

    if result == "win":
        await update_balance(user_id, bet)
        await message.answer(f"🎉 YUTDINGIZ! +{bet} coin")
    else:
        await update_balance(user_id, -bet)
        await message.answer(f"😢 YUTQAZDINGIZ! -{bet} coin")

    user_game_state[user_id] = None
