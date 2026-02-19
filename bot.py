import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 8537782289 # O'zingizning ID raqamingiz

logging.basicConfig(level=logging.INFO)

# Aiogram 3.x uchun Bot obyektini to'g'ri yaratish
bot = Bot(
    token=API_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# --- BAZANI SOZLASH ---
def init_db():
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        balance INTEGER DEFAULT 0, 
        referals INTEGER DEFAULT 0,
        invited_by INTEGER
    )""")
    conn.commit()
    conn.close()

init_db()

# --- ADMIN HOLATLARI ---
class AdminStates(StatesGroup):
    broadcast = State()
    add_money_id = State()
    add_money_amount = State()

# --- ASOSIY KLAVIATURA (Rasmda ko'ringan barcha tugmalar) ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛍 Xizmatlar"), types.KeyboardButton(text="📲 Nomer olish"))
    builder.row(types.KeyboardButton(text="🛒 Buyurtmalarim"), types.KeyboardButton(text="👥 Pul ishlash"))
    builder.row(types.KeyboardButton(text="💵 Hisobim"), types.KeyboardButton(text="💰 Hisob To'ldirish"))
    builder.row(types.KeyboardButton(text="📞 Murojaat"), types.KeyboardButton(text="☎️ Qo'llab-quvvatlash"))
    builder.row(types.KeyboardButton(text="🤝 Hamkorlik"))
    return builder.as_markup(resize_keyboard=True)

# --- START ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    ref_id = command.args
    
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        invited_by = int(ref_id) if ref_id and ref_id.isdigit() and int(ref_id) != user_id else None
        cursor.execute("INSERT INTO users (id, invited_by) VALUES (?, ?)", (user_id, invited_by))
        if invited_by:
            cursor.execute("UPDATE users SET referals = referals + 1, balance = balance + 500 WHERE id = ?", (invited_by,))
            try:
                await bot.send_message(invited_by, "✅ Sizda yangi referal! Balansingizga 500 so'm qo'shildi.")
            except: pass
        conn.commit()
    conn.close()

    text = (f"👋 <b>Assalomu alaykum! {message.from_user.first_name}</b>\n\n"
            f"🤖 @SaleSeenBot ga xush kelibsiz!\n\n"
            "Ushbu bot orqali ijtimoiy tarmoqlarga sifatli <b>NAKRUTKA</b> va boshqa xizmatlardan foydalanishingiz mumkin.")
    await message.answer(text, reply_markup=main_menu())

# --- FOYDALANUVCHI TUGMALARI ---
@dp.message(F.text == "💵 Hisobim")
async def profile(message: types.Message):
    conn = sqlite3.connect("sale_seen.db")
    res = conn.execute("SELECT balance, referals FROM users WHERE id = ?", (message.from_user.id,)).fetchone()
    conn.close()
    await message.answer(f"👤 <b>Profilingiz:</b>\n\n🆔 ID: <code>{message.from_user.id}</code>\n💰 Balans: <b>{res[0]} so'm</b>\n👥 Referallar: <b>{res[1]} ta</b>")

@dp.message(F.text == "🛍 Xizmatlar")
async def services(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🔵 Telegram", callback_data="s_tg"))
    builder.add(types.InlineKeyboardButton(text="🟣 Instagram", callback_data="s_inst"))
    builder.add(types.InlineKeyboardButton(text="⚫️ TikTok", callback_data="s_tt"))
    builder.adjust(1)
    await message.answer("👇 <b>Xizmat turini tanlang:</b>", reply_markup=builder.as_markup())

@dp.message(F.text == "👥 Pul ishlash")
async def earn(message: types.Message):
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={message.from_user.id}"
    await message.answer(f"🎁 <b>Do'stlarni taklif qilib pul ishlang!</b>\n\n🔗 Havolangiz:\n{link}")

@dp.message(F.text == "🤝 Hamkorlik")
async def collab(message: types.Message):
    await message.answer("🤝 <b>Hamkorlik bo'yicha adminga yozing:</b> @Admin_User")

# --- QOLGAN TUGMALAR ---
@dp.message(F.text.in_({"📲 Nomer olish", "🛒 Buyurtmalarim", "💰 Hisob To'ldirish", "📞 Murojaat", "☎️ Qo'llab-quvvatlash"}))
async def coming_soon(message: types.Message):
    await message.answer(f"⚙️ <b>{message.text}</b> bo'limi hozirda sozlanmoqda...")

# --- ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
        
