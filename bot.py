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
ADMIN_ID = 123456789 # O'z ID raqamingizni kiriting

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# --- BAZA (API kalitlarni saqlash uchun ustun qo'shildi) ---
def init_db():
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        balance INTEGER DEFAULT 0,
        api_key TEXT
    )""")
    conn.commit()
    conn.close()

init_db()

# --- ASOSIY MENYU ---
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
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        # Yangi foydalanuvchi uchun tasodifiy API kalit yaratish
        new_key = secrets.token_hex(16)
        cursor.execute("INSERT INTO users (id, api_key) VALUES (?, ?)", (user_id, new_key))
        conn.commit()
    conn.close()
    
    await message.answer(f"👋 Assalomu alaykum! {message.from_user.first_name}\n\n🤖 @SaleSeenBot ga xush kelibsiz!", reply_markup=main_menu())

# --- HAMKORLIK ASOSIY ---
@dp.message(F.text == "🤝 Hamkorlik")
async def collab_main(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="collab_smm"))
    builder.row(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="collab_nomer"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="collab_bot"))
    
    text = (
        "🤝 <b>Hamkorlik dasturi. Biz bilan yangi daromad manbaingizni yarating.</b>\n\n"
        "<i>Tushunmasangiz:</i> @SaleContact murojaat qilishingiz mumkin.\n\n"
        "📋 <b>Kerakli bo'limni tanlang:</b>"
    )
    await message.answer(text, reply_markup=builder.as_markup())

# --- SMM PANEL TIZIMI ---
@dp.callback_query(F.data == "collab_smm")
async def smm_panel(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔑 API Kalit", callback_data="show_api"),
        types.InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data="guides")
    )
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_collab"))
    
    text = "🔥 <b>SMM Panel - tizimi</b>\n\n📋 Ushbu tizim orqali siz SMM xizmatlariga API orqali buyurtma qilishingiz mumkin"
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- API KALIT BO'LIMI (RASMDAGI OXIRGI QISM) ---
@dp.callback_query(F.data.in_({"show_api", "refresh_api"}))
async def api_key_page(call: types.CallbackQuery):
    user_id = call.from_user.id
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    
    if call.data == "refresh_api":
        new_key = secrets.token_hex(16)
        cursor.execute("UPDATE users SET api_key = ? WHERE id = ?", (new_key, user_id))
        conn.commit()
    
    cursor.execute("SELECT api_key FROM users WHERE id = ?", (user_id,))
    api_key = cursor.fetchone()[0]
    conn.close()
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="♻️ API kalitni yangilash", callback_data="refresh_api"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="collab_smm"))
    
    text = (
        f"📌<b>Sizning API Manzilingiz</b>👇:\nhttps://saleseen.uz/api/v2\n\n"
        f"📋 <b>Sizning API kalitingiz</b>👇:\n<code>{api_key}</code>"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- ORQAGA QAYTISH ---
@dp.callback_query(F.data == "back_to_collab")
async def back_to_main_collab(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="collab_smm"))
    builder.row(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="collab_nomer"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="collab_bot"))
    
    text = "🤝 <b>Hamkorlik dasturi...</b>\n\n📋 <b>Kerakli bo'limni tanlang:</b>"
    await call.message.edit_text(text, reply_markup=builder.as_markup())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
