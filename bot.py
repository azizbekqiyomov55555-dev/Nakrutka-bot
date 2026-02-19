import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
import aiosqlite

TOKEN = "8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8"
ADMIN_ID = 8537782289

bot = Bot(TOKEN)
dp = Dispatcher()

user_state = {}

# ================= DATABASE =================

async def init_db():
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service TEXT,
            quantity INTEGER,
            price INTEGER,
            status TEXT
        )
        """)
        await db.commit()

async def add_user(uid):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("INSERT OR IGNORE INTO users(user_id) VALUES(?)", (uid,))
        await db.commit()

async def get_balance(uid):
    async with aiosqlite.connect("bot.db") as db:
        async with db.execute("SELECT balance FROM users WHERE user_id=?", (uid,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0

async def update_balance(uid, amount):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (amount, uid))
        await db.commit()

async def create_order(uid, service, quantity, price):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute(
            "INSERT INTO orders(user_id,service,quantity,price,status) VALUES(?,?,?,?,?)",
            (uid, service, quantity, price, "Jarayonda")
        )
        await db.commit()

# ================= START =================

@dp.message(CommandStart())
async def start(msg: Message):
    await add_user(msg.from_user.id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Xizmatlar", callback_data="services")],
        [InlineKeyboardButton(text="💰 Hisobim", callback_data="balance")],
        [InlineKeyboardButton(text="📦 Buyurtmalarim", callback_data="orders")],
        [InlineKeyboardButton(text="💵 Hisob to‘ldirish", callback_data="topup")]
    ])

    await msg.answer("👋 Xush kelibsiz!", reply_markup=kb)

# ================= SERVICES =================

services_list = {
    "Instagram Reklama": 50,
    "Telegram Reklama": 40,
    "Dizayn Xizmati": 100
}

@dp.callback_query(F.data == "services")
async def services(call):
    buttons = []
    for name in services_list:
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"service:{name}")])

    await call.message.edit_text(
        "Xizmatni tanlang:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )

@dp.callback_query(F.data.startswith("service:"))
async def select_service(call):
    service = call.data.split(":")[1]
    user_state[call.from_user.id] = {"service": service}

    await call.message.answer("Miqdor kiriting:")

# ================= ORDER FLOW =================

@dp.message()
async def process(msg: Message):
    uid = msg.from_user.id

    if uid not in user_state:
        return

    state = user_state[uid]

    if "quantity" not in state:
        if not msg.text.isdigit():
            await msg.answer("Raqam kiriting")
            return

        quantity = int(msg.text)
        price_per_unit = services_list[state["service"]]
        total_price = quantity * price_per_unit

        balance = await get_balance(uid)

        if balance < total_price:
            await msg.answer(f"❌ Balans yetarli emas.\nKerak: {total_price}\nBalans: {balance}")
            del user_state[uid]
            return

        await update_balance(uid, -total_price)
        await create_order(uid, state["service"], quantity, total_price)

        await msg.answer(f"✅ Buyurtma yaratildi!\nNarx: {total_price}")
        await bot.send_message(
            ADMIN_ID,
            f"Yangi buyurtma\nUser: {uid}\nXizmat: {state['service']}\nMiqdor: {quantity}\nNarx: {total_price}"
        )

        del user_state[uid]

# ================= BALANCE =================

@dp.callback_query(F.data == "balance")
async def balance(call):
    bal = await get_balance(call.from_user.id)
    await call.message.answer(f"💰 Balans: {bal}")

# ================= ORDERS =================

@dp.callback_query(F.data == "orders")
async def orders(call):
    async with aiosqlite.connect("bot.db") as db:
        async with db.execute("SELECT service,quantity,price,status FROM orders WHERE user_id=?", (call.from_user.id,)) as cur:
            data = await cur.fetchall()

    if not data:
        await call.message.answer("Buyurtmalar yo‘q")
    else:
        text = ""
        for s, q, p, st in data:
            text += f"{s}\nMiqdor: {q}\nNarx: {p}\nHolat: {st}\n\n"
        await call.message.answer(text)

# ================= ADMIN BALANCE ADD =================

@dp.message(F.text.startswith("/add"))
async def add_balance(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return

    parts = msg.text.split()
    uid = int(parts[1])
    amount = int(parts[2])

    await update_balance(uid, amount)
    await msg.answer("Balans qo‘shildi")

# ================= RUN =================

async def main():
    await init_db()
    print("PRO BOT ISHGA TUSHDI")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
