import logging
import sqlite3
import asyncio
import secrets
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# --- BAZA FUNKSIYALARI ---
def get_db_connection():
    conn = sqlite3.connect("sale_seen.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            balance INTEGER DEFAULT 0,
            api_key TEXT
        )""")

init_db()

# --- KLAVIATURALAR ---
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
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            conn.execute("INSERT INTO users (id, api_key) VALUES (?, ?)", (user_id, secrets.token_hex(16)))
    
    await message.answer(f"👋 Assalomu alaykum! {message.from_user.first_name}\n\n🤖 @SaleSeenBot ga xush kelibsiz!", reply_markup=main_menu())

# --- HAMKORLIK ---
@dp.message(F.text == "🤝 Hamkorlik")
async def collab_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="sect_smm"))
    builder.row(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="sect_nomer"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="sect_bot"))
    builder.adjust(1)
    
    text = "🤝 <b>Hamkorlik dasturi.</b>\n\n📋 <b>Kerakli bo'limni tanlang:</b>"
    await message.answer(text, reply_markup=builder.as_markup())

# --- SEKSIYALAR (SMM / NOMER) ---
@dp.callback_query(F.data.in_({"sect_smm", "sect_nomer"}))
async def section_handler(call: types.CallbackQuery):
    is_smm = call.data == "sect_smm"
    title = "🔥 SMM Panel - tizimi" if is_smm else "☎️ Nomer API - tizimi"
    prefix = "smm" if is_smm else "num"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔑 API Kalit", callback_data=f"api_view_{prefix}"),
        types.InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data=f"api_guide_{prefix}")
    )
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_collab"))
    
    text = f"<b>{title}</b>\n\n📋 Ushbu tizim orqali API buyurtmalar qilishingiz mumkin."
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- API KALITNI KO'RSATISH (Mana shu joyi ishlamayotgan edi) ---
@dp.callback_query(F.data.startswith("api_view_") | F.data.startswith("api_refresh_"))
async def api_display(call: types.CallbackQuery):
    user_id = call.from_user.id
    prefix = call.data.split("_")[-1] # smm yoki num
    
    with get_db_connection() as conn:
        if "refresh" in call.data:
            new_key = secrets.token_hex(16)
            conn.execute("UPDATE users SET api_key = ? WHERE id = ?", (new_key, user_id))
        
        user = conn.execute("SELECT api_key FROM users WHERE id = ?", (user_id,)).fetchone()
        api_key = user['api_key']

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="♻️ API kalitni yangilash", callback_data=f"api_refresh_{prefix}"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"sect_{"smm" if prefix=="smm" else "nomer"}"))
    
    text = (
        f"📌 <b>Sizning API Manzilingiz</b> 👇:\n<code>https://saleseen.uz/api/v2</code>\n\n"
        f"📋 <b>Sizning API kalitingiz</b> 👇:\n<code>{api_key}</code>"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- ORQAGA QAYTISH ---
@dp.callback_query(F.data == "back_collab")
async def back_to_collab(call: types.CallbackQuery):
    await collab_menu(call.message)
    await call.message.delete()

# --- ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
