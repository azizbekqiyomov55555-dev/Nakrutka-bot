import asyncio
import random
import sqlite3
import time
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

TOKEN = "8318931210:AAFJLBgfF2_reXxXWpWjb8NjsuveWxYIVjY"
ADMIN_ID = 8537782289  # <-- o'zingni ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== DATABASE =====
conn = sqlite3.connect("casino.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 1000,
    last_bonus INTEGER DEFAULT 0,
    referred_by INTEGER DEFAULT NULL
)
""")

conn.commit()

# ===== MENU =====
def menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Coin Flip"), KeyboardButton(text="🎲 Dice")],
            [KeyboardButton(text="🔢 High/Low"), KeyboardButton(text="🎯 Guess 1-10")],
            [KeyboardButton(text="🎰 Slot"), KeyboardButton(text="🪙 Double")],
            [KeyboardButton(text="🎡 Wheel"), KeyboardButton(text="💣 Mines")],
            [KeyboardButton(text="🐎 Horse"), KeyboardButton(text="🎁 Bonus")],
            [KeyboardButton(text="🏆 Top"), KeyboardButton(text="👤 Profil")]
        ],
        resize_keyboard=True
    )

game_state = {}

# ===== START + REFERRAL =====
@dp.message(CommandStart())
async def start(message: Message):
    args = message.text.split()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,))
    user = cursor.fetchone()

    if not user:
        referred_by = None
        if len(args) > 1:
            referred_by = int(args[1])

        cursor.execute(
            "INSERT INTO users (user_id, referred_by) VALUES (?,?)",
            (message.from_user.id, referred_by)
        )
        conn.commit()

        if referred_by:
            cursor.execute("UPDATE users SET balance = balance + 500 WHERE user_id=?", (referred_by,))
            conn.commit()

    await message.answer("🎰 PRO Casino Botga xush kelibsiz!", reply_markup=menu())

# ===== PROFIL =====
@dp.message(F.text == "👤 Profil")
async def profile(message: Message):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (message.from_user.id,))
    bal = cursor.fetchone()[0]

    link = f"https://t.me/{(await bot.get_me()).username}?start={message.from_user.id}"

    await message.answer(
        f"👤 ID: {message.from_user.id}\n"
        f"💰 Balans: {bal} coin\n\n"
        f"👥 Referral link:\n{link}"
    )

# ===== TOP =====
@dp.message(F.text == "🏆 Top")
async def top_users(message: Message):
    cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    users = cursor.fetchall()

    text = "🏆 TOP 10:\n\n"
    for i, user in enumerate(users, start=1):
        text += f"{i}. {user[0]} — {user[1]} coin\n"

    await message.answer(text)

# ===== BONUS (24 soat) =====
@dp.message(F.text == "🎁 Bonus")
async def bonus(message: Message):
    cursor.execute("SELECT last_bonus FROM users WHERE user_id=?", (message.from_user.id,))
    last_bonus = cursor.fetchone()[0]

    now = int(time.time())

    if now - last_bonus < 86400:
        await message.answer("⏳ Bonusni 24 soatda 1 marta olasiz!")
        return

    cursor.execute("UPDATE users SET balance = balance + 1000, last_bonus=? WHERE user_id=?",
                   (now, message.from_user.id))
    conn.commit()

    await message.answer("🎁 +1000 coin bonus!")

# ===== ADMIN PANEL =====
@dp.message(F.text.startswith("/add"))
async def add_balance(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    _, user_id, amount = message.text.split()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?",
                   (int(amount), int(user_id)))
    conn.commit()
    await message.answer("✅ Balans qo‘shildi!")

# ===== GAME START =====
games = {
    "🎮 Coin Flip": 0.48,
    "🎲 Dice": 0.50,
    "🔢 High/Low": 0.48,
    "🎯 Guess 1-10": 0.45,
    "🎰 Slot": 0.30,
    "🪙 Double": 0.45,
    "🎡 Wheel": 0.40,
    "💣 Mines": 0.35,
    "🐎 Horse": 0.38,
}

@dp.message(F.text.in_(games.keys()))
async def game_start(message: Message):
    game_state[message.from_user.id] = message.text
    await message.answer("💵 Stavka kiriting:")

# ===== GAME LOGIC =====
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
    if not game:
        return

    win_chance = games[game]
    win = random.random() < win_chance

    if win:
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (bet, user_id))
        text = f"🎉 YUTDINGIZ! +{bet}"
    else:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (bet, user_id))
        text = f"😢 YUTQAZDINGIZ! -{bet}"

    conn.commit()
    game_state[user_id] = None

    await message.answer(text)

# ===== RUN =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
