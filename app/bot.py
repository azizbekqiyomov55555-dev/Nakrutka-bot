import os
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from app.db import init_db, add_user, get_user, update_balance
from app.keyboards import main_menu

TOKEN = ("8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await add_user(message.from_user.id)
    await message.answer("🎰 Casino botga xush kelibsiz!", reply_markup=main_menu())

@dp.message(lambda msg: msg.text == "👤 Profil")
async def profile_handler(message: Message):
    user = await get_user(message.from_user.id)
    balance = user[0] if user else 0
    await message.answer(f"💰 Balans: {balance} coin")

@dp.message(lambda msg: msg.text == "🎮 Coin Flip")
async def coinflip_start(message: Message):
    await message.answer("Stavka miqdorini kiriting (masalan 100):")

@dp.message()
async def handle_bet(message: Message):
    if message.text.isdigit():
        bet = int(message.text)
        user = await get_user(message.from_user.id)

        if not user:
            return

        balance = user[0]

        if bet > balance:
            await message.answer("❌ Balans yetarli emas!")
            return

        result = random.choice(["win", "lose"])

        if result == "win":
            await update_balance(message.from_user.id, bet)
            await message.answer(f"🎉 YUTDINGIZ! +{bet} coin")
        else:
            await update_balance(message.from_user.id, -bet)
            await message.answer(f"😢 YUTQAZDINGIZ! -{bet} coin")
