import asyncio
import random
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

TOKEN = "8318931210:AAFJLBgfF2_reXxXWpWjb8NjsuveWxYIVjY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== DATABASE =====
conn = sqlite3.connect("casino.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 1000
)
""")
conn.commit()

# ===== MENU =====
def menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Coin Flip"), KeyboardButton(text="🎲 Dice")],
            [KeyboardButton(text="🔢 High/Low"), KeyboardButton(text="🎯 Guess")],
            [KeyboardButton(text="🎰 Slot"), KeyboardButton(text="🪙 Double")],
            [KeyboardButton(text="🎡 Wheel"), KeyboardButton(text="💣 Mines")],
            [KeyboardButton(text="🐎 Horse"), KeyboardButton(text="🎁 Bonus")],
            [KeyboardButton(text="👤 Profil")]
        ],
        resize_keyboard=True
    )

game_state = {}

# ===== START =====
@dp.message(CommandStart())
async def start(message: Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()
    await message.answer("🎰 Casino botga xush kelibsiz!", reply_markup=menu())

# ===== PROFIL =====
@dp.message(F.text == "👤 Profil")
async def profile(message: Message):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (message.from_user.id,))
    bal = cursor.fetchone()[0]
    await message.answer(f"💰 Balans: {bal} coin")

# ===== BONUS =====
@dp.message(F.text == "🎁 Bonus")
async def bonus(message: Message):
    cursor.execute("UPDATE users SET balance = balance + 500 WHERE user_id=?", (message.from_user.id,))
    conn.commit()
    await message.answer("🎁 +500 coin bonus!")

# ===== GAME START =====
games = {
    "🎮 Coin Flip": "coin",
    "🎲 Dice": "dice",
    "🔢 High/Low": "highlow",
    "🎯 Guess": "guess",
    "🎰 Slot": "slot",
    "🪙 Double": "double",
    "🎡 Wheel": "wheel",
    "💣 Mines": "mines",
    "🐎 Horse": "horse",
}

@dp.message(F.text.in_(games.keys()))
async def game_start(message: Message):
    game_state[message.from_user.id] = games[message.text]
    await message.answer("💵 Stavka kiriting:")

# ===== HANDLE BET =====
@dp.message()
async def play(message: Message):
    if not message.text.isdigit():
        return

    bet = int(message.text)
    user_id = message.from_user.id

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    bal = cursor.fetchone()[0]

    if bet <= 0 or bet > bal:
        await message.answer("❌ Noto‘g‘ri stavka!")
        return

    game = game_state.get(user_id)
    win = False

    if game == "coin":
        win = random.random() < 0.48

    elif game == "dice":
        win = random.randint(1,6) >= 4

    elif game == "highlow":
        win = random.random() < 0.48

    elif game == "guess":
        win = random.randint(1,10) > 5

    elif game == "slot":
        win = random.random() < 0.30

    elif game == "double":
        win = random.random() < 0.45

    elif game == "wheel":
        win = random.random() < 0.40

    elif game == "mines":
        win = random.random() < 0.35

    elif game == "horse":
        win = random.random() < 0.38

    if win:
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (bet, user_id))
        await message.answer(f"🎉 YUTDINGIZ! +{bet}")
    else:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (bet, user_id))
        await message.answer(f"😢 YUTQAZDINGIZ! -{bet}")

    conn.commit()
    game_state[user_id] = None

# ===== RUN =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
