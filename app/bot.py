import asyncio
import random
import sqlite3
import time
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

TOKEN = "8318931210:AAFJLBgfF2_reXxXWpWjb8NjsuveWxYIVjY"
ADMIN_ID = 8537782289

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
    referred_by INTEGER DEFAULT NULL,
    banned INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS withdraws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    status TEXT DEFAULT 'pending'
)
""")

conn.commit()

# ===== MENU =====
def main_menu(user_id):
    keyboard = [
        [KeyboardButton(text="🎮 Coin Flip"), KeyboardButton(text="🎲 Dice")],
        [KeyboardButton(text="🔢 High/Low"), KeyboardButton(text="🎯 Guess 1-10")],
        [KeyboardButton(text="🎰 Slot"), KeyboardButton(text="🪙 Double")],
        [KeyboardButton(text="🎡 Wheel"), KeyboardButton(text="💣 Mines")],
        [KeyboardButton(text="🐎 Horse"), KeyboardButton(text="🎁 Bonus")],
        [KeyboardButton(text="🏆 Top"), KeyboardButton(text="💸 Withdraw")],
        [KeyboardButton(text="👤 Profil")]
    ]

    if user_id == ADMIN_ID:
        keyboard.append([KeyboardButton(text="👑 Admin Panel")])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ===== GAME SETTINGS =====
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

game_state = {}
withdraw_state = {}

# ===== START =====
@dp.message(CommandStart())
async def start_handler(message: Message):
    cursor.execute("SELECT banned FROM users WHERE user_id=?", (message.from_user.id,))
    banned = cursor.fetchone()

    if banned and banned[0] == 1:
        await message.answer("🚫 Siz bloklangansiz.")
        return

    args = message.text.split()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (message.from_user.id,))
    user = cursor.fetchone()

    if not user:
        referred_by = None
        if len(args) > 1 and args[1].isdigit():
            referred_by = int(args[1])

        cursor.execute(
            "INSERT INTO users (user_id, referred_by) VALUES (?,?)",
            (message.from_user.id, referred_by)
        )
        conn.commit()

        if referred_by and referred_by != message.from_user.id:
            cursor.execute("UPDATE users SET balance = balance + 500 WHERE user_id=?", (referred_by,))
            conn.commit()

    await message.answer("🎰 Mega Casino Botga xush kelibsiz!", reply_markup=main_menu(message.from_user.id))

# ===== PROFIL =====
@dp.message(F.text == "👤 Profil")
async def profile_handler(message: Message):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (message.from_user.id,))
    bal = cursor.fetchone()[0]

    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"

    await message.answer(
        f"👤 ID: {message.from_user.id}\n"
        f"💰 Balans: {bal} coin\n\n"
        f"👥 Referral link:\n{ref_link}"
    )

# ===== TOP =====
@dp.message(F.text == "🏆 Top")
async def top_handler(message: Message):
    cursor.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    users = cursor.fetchall()

    text = "🏆 TOP 10:\n\n"
    for i, user in enumerate(users, 1):
        text += f"{i}. {user[0]} — {user[1]} coin\n"

    await message.answer(text)

# ===== BONUS =====
@dp.message(F.text == "🎁 Bonus")
async def bonus_handler(message: Message):
    cursor.execute("SELECT last_bonus FROM users WHERE user_id=?", (message.from_user.id,))
    last_bonus = cursor.fetchone()[0]
    now = int(time.time())

    if now - last_bonus < 86400:
        await message.answer("⏳ 24 soatda 1 marta!")
        return

    cursor.execute("UPDATE users SET balance = balance + 1000, last_bonus=? WHERE user_id=?",
                   (now, message.from_user.id))
    conn.commit()

    await message.answer("🎁 +1000 coin!")

# ===== GAME START =====
@dp.message(F.text.in_(games.keys()))
async def game_start(message: Message):
    game_state[message.from_user.id] = message.text
    await message.answer("💵 Stavka kiriting:")

# ===== WITHDRAW =====
@dp.message(F.text == "💸 Withdraw")
async def withdraw_start(message: Message):
    withdraw_state[message.from_user.id] = True
    await message.answer("💰 Qancha coin?")

# ===== ADMIN PANEL =====
@dp.message(F.text == "👑 Admin Panel")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(balance) FROM users")
    total_balance = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM withdraws WHERE status='pending'")
    pending = cursor.fetchone()[0]

    await message.answer(
        f"👑 ADMIN PANEL\n\n"
        f"👥 Users: {users}\n"
        f"💰 Total Balance: {total_balance}\n"
        f"💸 Pending Withdraw: {pending}"
    )

# ===== MAIN HANDLER =====
@dp.message()
async def universal_handler(message: Message):
    user_id = message.from_user.id

    if withdraw_state.get(user_id):
        if not message.text.isdigit():
            return

        amount = int(message.text)

        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        bal = cursor.fetchone()[0]

        if amount <= 0 or amount > bal:
            await message.answer("❌ Noto‘g‘ri summa!")
            return

        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (amount, user_id))
        cursor.execute("INSERT INTO withdraws (user_id, amount) VALUES (?,?)", (user_id, amount))
        conn.commit()

        withdraw_state[user_id] = False

        await message.answer("✅ So‘rov yuborildi.")
        await bot.send_message(ADMIN_ID, f"💸 Withdraw\nUser: {user_id}\nAmount: {amount}")
        return

    if not message.text.isdigit():
        return

    bet = int(message.text)

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    bal = cursor.fetchone()[0]

    if bet <= 0 or bet > bal:
        await message.answer("❌ Noto‘g‘ri stavka!")
        return

    game = game_state.get(user_id)
    if not game:
        return

    win = random.random() < games[game]

    if win:
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (bet, user_id))
        text = f"🎉 YUTDINGIZ +{bet}"
    else:
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id=?", (bet, user_id))
        text = f"😢 YUTQAZDINGIZ -{bet}"

    conn.commit()
    game_state[user_id] = None
    await message.answer(text)

# ===== RUN =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
