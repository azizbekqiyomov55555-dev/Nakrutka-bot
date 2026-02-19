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

# Railway xatosini oldini olish uchun DefaultBotProperties ishlatildi
bot = Bot(
    token=API_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# --- BAZA SOZLAMALARI ---
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

# --- ASOSIY REPLAY MENYU ---
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
        new_key = secrets.token_hex(16)
        cursor.execute("INSERT INTO users (id, api_key) VALUES (?, ?)", (user_id, new_key))
        conn.commit()
    conn.close()
    
    welcome_text = (
        f"👋 <b>Assalomu alaykum! {message.from_user.first_name}</b>\n\n"
        f"💙 @SaleSeenBot ga xush kelibsiz!\n\n"
        f"Ushbu bot orqali siz barcha platformalarga shuningdek:\n"
        f"🔵 Telegram,\n📸 Instagram,\n🎬 TikTok,\n🔴 YouTube va boshqa tarmoqlarga "
        f"sifatli va hamyonbop <b>NAKRUTKA</b> va boshqa xizmatlardan foydalanishingiz mumkin."
    )
    await message.answer(welcome_text, reply_markup=main_menu())

# --- HAMKORLIK ASOSIY (Rasm 4 va 5 ga mos) ---
@dp.message(F.text == "🤝 Hamkorlik")
async def collab_main(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="collab_smm"))
    builder.row(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="collab_nomer"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="collab_bot"))
    builder.adjust(1)
    
    text = (
        "🤝 <b>Hamkorlik dasturi. Biz bilan yangi daromad manbaingizni yarating.</b>\n\n"
        "<i>Tushunmasangiz:</i> @SaleContact murojaat qilishingiz mumkin.\n\n"
        "📋 <b>Kerakli bo'limni tanlang:</b>"
    )
    await message.answer(text, reply_markup=builder.as_markup())

# --- SMM PANEL TIZIMI (Rasm 6 ga mos) ---
@dp.callback_query(F.data == "collab_smm")
async def smm_panel(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔑 API Kalit", callback_data="show_api_smm"),
        types.InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data="guides_smm")
    )
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_collab"))
    
    text = "🔥 <b>SMM Panel - tizimi</b>\n\n📋 Ushbu tizim orqali siz SMM xizmatlariga API orqali buyurtma qilishingiz mumkin"
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- NOMER API TIZIMI (Rasm 10 ga mos) ---
@dp.callback_query(F.data == "collab_nomer")
async def nomer_api_panel(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="🔑 API Kalit", callback_data="show_api_nomer"),
        types.InlineKeyboardButton(text="💼 Qo'llanmalar", callback_data="guides_nomer")
    )
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_collab"))
    
    text = "☎️ <b>Nomer API - tizimi</b>\n\n📋 Ushbu tizim orqali siz Tayyor Akkauntlarga API olishingiz mumkin"
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- API KALIT VA YANGILASH (Rasm 7, 8, 9 ga mos) ---
@dp.callback_query(F.data.startswith("show_api_") | F.data.startswith("refresh_api_"))
async def api_key_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    # Qaysi bo'limdan kelganini aniqlash (smm yoki nomer)
    current_section = "collab_smm" if "smm" in call.data else "collab_nomer"
    
    conn = sqlite3.connect("sale_seen.db")
    cursor = conn.cursor()
    
    if "refresh_api_" in call.data:
        new_key = secrets.token_hex(16)
        cursor.execute("UPDATE users SET api_key = ? WHERE id = ?", (new_key, user_id))
        conn.commit()
    
    cursor.execute("SELECT api_key FROM users WHERE id = ?", (user_id,))
    api_key = cursor.fetchone()[0]
    conn.close()
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="♻️ API kalitni yangilash", callback_data=f"refresh_api_{current_section}"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data=current_section))
    
    if "guides" in call.data or (hasattr(call, 'message') and "dokumentlar" in call.message.text.lower()):
        text = f"Api urllar va dokumentlar 💼 Qo'llanmalar bo'limida.\n\n📋 <b>Sizning API kalitingiz</b> 👇:\n<code>{api_key}</code>"
    else:
        text = (
            f"📌 <b>Sizning API Manzilingiz</b> 👇:\n<code>https://saleseen.uz/api/v2</code>\n\n"
            f"📋 <b>Sizning API kalitingiz</b> 👇:\n<code>{api_key}</code>"
        )
    
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- QO'LLANMALAR (Rasm 9 ga mos) ---
@dp.callback_query(F.data.startswith("guides_"))
async def guides_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    current_section = "collab_smm" if "smm" in call.data else "collab_nomer"
    
    conn = sqlite3.connect("sale_seen.db")
    api_key = conn.execute("SELECT api_key FROM users WHERE id = ?", (user_id,)).fetchone()[0]
    conn.close()
    
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="♻️ API kalitni yangilash", callback_data=f"refresh_api_{current_section}"))
    builder.row(types.InlineKeyboardButton(text="🔙 Orqaga", callback_data=current_section))
    
    text = f"Api urllar va dokumentlar 💼 Qo'llanmalar bo'limida.\n\n📋 <b>Sizning API kalitingiz</b> 👇:\n<code>{api_key}</code>"
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- ORQAGA QAYTISH ---
@dp.callback_query(F.data == "back_to_collab")
async def back_to_collab_handler(call: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🔥 SMM Panel API", callback_data="collab_smm"))
    builder.row(types.InlineKeyboardButton(text="☎️ TG Nomer API", callback_data="collab_nomer"))
    builder.row(types.InlineKeyboardButton(text="🤖 SMM Bot Yaratish", callback_data="collab_bot"))
    builder.adjust(1)
    
    text = "🤝 <b>Hamkorlik dasturi...</b>\n\n📋 <b>Kerakli bo'limni tanlang:</b>"
    await call.message.edit_text(text, reply_markup=builder.as_markup())

# --- ISHGA TUSHIRISH ---
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
    
