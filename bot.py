import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 8537782289 # O'zingizning ID raqamingiz

logging.basicConfig(level=logging.INFO)

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

# --- ASOSIY REPLAY KLAVIATURA ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛍 Xizmatlar"), types.KeyboardButton(text="📲 Nomer olish"))
    builder.row(types.KeyboardButton(text="🛒 Buyurtmalarim"), types.KeyboardButton(text="👥 Pul ishlash"))
    builder.row(types.KeyboardButton(text="💵 Hisobim"), types.KeyboardButton(text="💰 Hisob To'ldirish"))
    builder.row(types.KeyboardButton(text="📞 Murojaat"), types.KeyboardButton(text="☎️ Qo'llab-quvvatlash"))
    builder.row(types.KeyboardButton(text="🤝 Hamkorlik"))
    return builder.as_markup(resize_keyboard=True)

# --- START KOMANDASI ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
        conn.commit()
    conn.close()

    text = (f"👋 <b>Assalomu alaykum! {message.from_user.first_name}</b>\n\n"
            f"🤖 @SaleSeenBot ga xush kelibsiz!")
    await message.answer(text, reply_markup=main_menu())

# --- HAMKORLIK BO'LIMI (YANGILANGAN) ---
@dp.message(F.text == "🤝 Hamkorlik")
async def collab_section(message: types.Message):
    # Inline tugmalarni rasmga moslab yaratamiz
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="collab_smm"))
    builder.add(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="collab_nomer"))
    builder.add(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="collab_bot"))
    builder.adjust(1) # Har bir tugma alohida qatorda

    text = (
        "🤝 <b>Hamkorlik dasturi. Biz bilan yangi daromad manbaingizni yarating.</b>\n\n"
        "<i>Tushunmasangiz:</i> @SaleContact murojaat qilishingiz mumkin.\n\n"
        "📋 <b>Kerakli bo'limni tanlang:</b>"
    )
    
    await message.answer(text, reply_markup=builder.as_markup())

# --- HAMKORLIK TUGMALARI UCHUN JAVOBLAR (CALLBACK) ---
@dp.callback_query(F.data.startswith("collab_"))
async def collab_callback(call: types.CallbackQuery):
    if call.data == "collab_smm":
        await call.answer("SMM Panel API bo'limi tanlandi", show_alert=True)
    elif call.data == "collab_nomer":
        await call.answer("TG Nomer API bo'limi tanlandi", show_alert=True)
    elif call.data == "collab_bot":
        await call.answer("SMM Bot Yaratish bo'limi tanlandi", show_alert=True)

# --- QOLGAN FUNKSIYALAR ---
@dp.message(F.text == "💵 Hisobim")
async def profile(message: types.Message):
    conn = sqlite3.connect("sale_seen.db")
    res = conn.execute("SELECT balance FROM users WHERE id = ?", (message.from_user.id,)).fetchone()
    conn.close()
    await message.answer(f"💰 Balansingiz: <b>{res[0]} so'm</b>")

# --- ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
        
