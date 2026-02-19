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
ADMIN_ID = 8537782289 # Siz bergan yangi ID

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# --- BAZA ---
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

# --- REPLAY MENYULAR ---
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛍 Xizmatlar"), types.KeyboardButton(text="📲 Nomer olish"))
    builder.row(types.KeyboardButton(text="🛒 Buyurtmalarim"), types.KeyboardButton(text="👥 Pul ishlash"))
    builder.row(types.KeyboardButton(text="💵 Hisobim"), types.KeyboardButton(text="💰 Hisob To'ldirish"))
    builder.row(types.KeyboardButton(text="📞 Murojaat"), types.KeyboardButton(text="☎️ Qo'llab-quvvatlash"))
    builder.row(types.KeyboardButton(text="🤝 Hamkorlik"))
    return builder.as_markup(resize_keyboard=True)

def nomer_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="📞 Telegram Akauntlar"), types.KeyboardButton(text="☎️ Boshqa Tarmoqlar"))
    builder.row(types.KeyboardButton(text="Bosh sahifa ⬆️"))
    return builder.as_markup(resize_keyboard=True)

# --- START ---
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            conn.execute("INSERT INTO users (id, api_key) VALUES (?, ?)", (user_id, secrets.token_hex(16)))
    
    welcome_text = (
        f"👋 <b>Assalomu alaykum! {message.from_user.first_name}</b>\n\n"
        f"💙 @SaleSeenBot ga xush kelibsiz!\n\n"
        f"💻 Ushbu bot orqali siz barcha platformalarga nuktka xizmatlarini olishingiz mumkin."
    )
    await message.answer(welcome_text, reply_markup=main_menu())

# --- NOMER OLISH BO'LIMI ---
@dp.message(F.text == "📲 Nomer olish")
async def nomer_olish_start(message: types.Message):
    await message.answer("👇 Kerakli tarmoqni tanlang.", reply_markup=nomer_menu())

# --- TELEGRAM AKAUNTLAR (OXIRGI RASMGA MOS) ---
@dp.message(F.text == "📞 Telegram Akauntlar")
async def tg_akauntlar(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Davlatlar ro'yxati (Rasmga mos)
    davlatlar = [
        ("Bangladesh 🇧🇩 - 8958", "buy_8958"), ("Hindiston 🇮🇳 - 11197", "buy_11197"),
        ("Keniya 🇰🇪 - 11197", "buy_11197k"), ("Kolumbiya 🇨🇴 - 12317", "buy_12317"),
        ("Azerbaijan 🇦🇿 - 13437", "buy_13437"), ("Dominikana 🇩🇴 - 13437", "buy_13437d"),
        ("Shri Lanka 🇱🇰 - 14556", "buy_14556"), ("Marokash 🇲🇦 - 14556", "buy_14556m"),
        ("Tanzaniya 🇹🇿 - 14556", "buy_14556t"), ("Zambiya 🇿🇲 - 14556", "buy_14556z")
    ]
    
    for text, callback in davlatlar:
        builder.add(types.InlineKeyboardButton(text=text, callback_data=callback))
    
    builder.adjust(2) # 2 tadan qilib joylash
    
    # Pastki boshqaruv tugmalari
    builder.row(types.InlineKeyboardButton(text="🥷 Admin orqali nomer olish", url="https://t.me/SaleContact"))
    builder.row(
        types.InlineKeyboardButton(text="1/9", callback_data="none"),
        types.InlineKeyboardButton(text="⏩ Keyingi", callback_data="next_page")
    )
    
    text = (
        "📞 <b>Ushbu davlat raqamlari faqat Telegram akaunt ochish uchun beriladi.</b>\n\n"
        "🛍 <b>Topilgan davlatlar ro'yxati:</b>"
    )
    await message.answer(text, reply_markup=builder.as_markup())

@dp.message(F.text == "Bosh sahifa ⬆️")
async def back_to_home(message: types.Message):
    await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=main_menu())

# --- HAMKORLIK BO'LIMI ---
@dp.message(F.text == "🤝 Hamkorlik")
async def collab_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="sect_smm"))
    builder.row(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="sect_nomer"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="sect_bot"))
    builder.adjust(1)
    
    text = (
        "🤝 <b>Hamkorlik dasturi. Biz bilan yangi daromad manbaingizni yarating.</b>\n\n"
        "<i>Tushunmasangiz:</i> @SaleContact murojaat qilishingiz mumkin."
    )
    await message.answer(text, reply_markup=builder.as_markup())

# --- API HANDLERLARI ---
@dp.callback_query(F.data.in_({"sect_smm", "sect_nomer"}))
async def section_handler(call: types.CallbackQuery):
    prefix = "smm" if call.data == "sect_smm" else "num"
    title = "🔥 SMM Panel - tizimi" if prefix == "smm" else "☎️ Nomer API - tizimi"
    
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔑 API Kalit", callback_data=f"api_view_{prefix}"),
        types.InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data=f"api_guide_{prefix}")
    )
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_collab"))
    
    await call.message.edit_text(f"<b>{title}</b>\n\n📋 Tizim orqali API buyurtma qilishingiz mumkin.", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("api_view_"))
async def api_display(call: types.CallbackQuery):
    user_id = call.from_user.id
    with get_db_connection() as conn:
        api_key = conn.execute("SELECT api_key FROM users WHERE id = ?", (user_id,)).fetchone()['api_key']

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="♻️ API kalitni yangilash", callback_data=f"api_refresh_{call.data.split('_')[-1]}"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_collab"))
    
    text = f"📌 <b>Sizning API Manzilingiz</b>:\n<code>https://saleseen.uz/api/v2</code>\n\n📋 <b>API kalitingiz</b>:\n<code>{api_key}</code>"
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
    
