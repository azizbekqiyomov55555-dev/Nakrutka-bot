import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message

TOKEN = ("8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Salom 👋 Bot ishlayapti!")

async def main():
    print("Bot ishga tushdi")
    await dp.start_polling(bot)
