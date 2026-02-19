import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- SOZLAMALAR ---
API_TOKEN = '8066717720:AAEe3NoBcug1rTFT428HEBmJriwiutyWtr8'
ADMIN_ID = 123456789 

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# --- BAZA ---
def init_db():
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

init_db()

# --- REPLAY MENYU ---
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
    await message.answer(f"👋 Assalomu alaykum! {message.from_user.first_name}\n\n🤖 @SaleSeenBot ga xush kelibsiz!", reply_markup=main_menu())

# --- 1-BOSQICH: HAMKORLIK MENYUSI ---
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

# --- 2-BOSQICH: SMM PANEL TIZIMI (RASMDAGI QISM) ---
@dp.callback_query(F.data == "collab_smm")
async def smm_panel_system(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔑 API Kalit", callback_data="api_key"),
        types.InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data="guides")
    )
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_collab"))
    
    text = (
        "🔥 <b>SMM Panel - tizimi</b>\n\n"
        "📋 Ushbu tizim orqali siz SMM xizmatlariga API orqali buyurtma qilishingiz mumkin"
    )
    
    # Xabarni tahrirlash (Edit) orqali yangi menyuga o'tamiz
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- 3-BOSQICH: ORQAGA QAYTISH FUNKSIYASI ---
@dp.callback_query(F.data == "back_to_collab")
async def back_handler(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="collab_smm"))
    builder.row(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="collab_nomer"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="collab_bot"))
    
    text = (
        "🤝 <b>Hamkorlik dasturi. Biz bilan yangi daromad manbaingizni yarating.</b>\n\n"
        "<i>Tushunmasangiz:</i> @SaleContact murojaat qilishingiz mumkin.\n\n"
        "📋 <b>Kerakli bo'limni tanlang:</b>"
    )
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- ASOSIY LOOP ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
    
